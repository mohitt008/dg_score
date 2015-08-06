(function ($) {
  $.fn.taggify = function (idd, segs, data_ob) {
    jq_name_obj = this;
    
    String.prototype.format = String.prototype.f = function () {
      var s = this, i = arguments.length;

      while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
      }
      return s;
    };
    
    function showTag(x, y) {
      $('.tag_list').css("left",x-200);
      $('.tag_list').css("top",y-20);
      $('.tag_list').focus();
    }

    function bindMenuSnapping() {
      $(document).click(function() {
        $('.tag_list').css("left","-9999px");
        $('.address_element').removeClass( "ui-selected" );
      });

      $(".address").click(function(e) {
        e.stopPropagation();
        return false;
      });
    }  

    function resetTags() {
      $('input:checkbox').removeAttr('checked');
      jq_name_obj.children().removeClass('ui-selected tagged').removeAttr('style').removeAttr('tag')
    }

    function setUpAddress(content_list) {
      var span_text = "<span class='address_element' tabindex='{0}'><abc>{1}</abc></span>";
      total_string = "";
      for (i = 0; i < content_list.length; i++) {
          total_string += span_text.f(i+1,content_list[i])
      }
      var tags = $('#tag_template').html();
      jq_name_obj.html(total_string);
      $(tags).insertAfter(jq_name_obj);
      $("<div class='tooltip'>Tooltip Box</div>").insertAfter('.address_element')
    }

    function getRandomColor () {
//      var hex = Math.floor(0.3*Math.random() * 0xFFFFFF);
//      var color = "#" + ("000000" + hex.toString(16)).substr(-6);
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    function tagItem(obj) {
      var tag_type = $(obj).attr('tagtype');
      $('.ui-selected').attr('tag',tag_type);
      $( "span[tag]").addClass('tagged');
      $.each($('.ui-selected'), function() {
        var addr_elem = $(this);
        var tooltip_obj = $(this).next();
        tooltip_obj.text(addr_elem.attr('tag'));
        tooltip_obj.css({
          'position':'absolute',
          'display': 'block',
          'left' : addr_elem.offset().left + addr_elem.outerWidth( false )/2 - tooltip_obj.outerWidth( false )/2 - 215,
          'top' : addr_elem.offset().top - 10
        });
      });
      // ---------------Coloring logic-------------------
      var all_elements = $( "span[tag]");
      $.each(all_elements, function(elem_obj){
        if ($(this).attr('tag') == tag_type)
          {
            $(this).css({
              'background-color': getRandomColor()
            });
          }
      })
    }

    function sendTagsAJAX(tags, dang, xray, dirty,skipped) {
      var date = new Date();
      data_ob.epoch = date.getTime();
      data_ob['id'] = idd;
      data_ob['tags'] = tags;
      data_ob['is_dang'] = dang;
      data_ob['is_xray'] = xray;
      data_ob['is_dirty'] = dirty;
      data_ob['is_skipped'] = skipped;
      return $.ajax({
        url: '/cat-ui/set-tags',
        dataType: 'json',
        type: 'POST', //make query POST
        contentType: 'application/json',
        data: JSON.stringify(data_ob)
      });
    }

    function sendTags(tags, is_dang, is_xray, is_dirty, is_skipped) {

      sendTagsAJAX(tags, is_dang, is_xray, is_dirty,is_skipped).done(function(data) {
        console.log('next product-name data: ', data);
        if(data.error) {
            $.notify(data.error, { position:"bottom-right" });
            $("#tag-products").css("display", "none");
        }
        else {
            resetTags();
            $('#org_prod_name').html(data.prod_name);
            $("#vendor_name").html(data['vendor']);
            $("#vendor_name").attr("href", data['prod_url']);
            $('#category').html(data.prod_cat);
            $('#sub-category').html(data.prod_subcat);
            $('#tag-count').html(data.tag_count);

            var attrs="";
            if (!jQuery.isEmptyObject(data['taglist'])) {
                $.each(data['taglist'], function (attr, code) {
                    attrs += '<a href="#" tagtype ="' + code + '"><span class="tag_text">' + attr + '</span></a>';
                });
            }
            $(".extra-attrs").html(attrs);

            id = data['id'];
            prod_seg = JSON.parse(data.prod_seg);
            if ('vendor' in data_ob)
                data_obj = {'vendor': data_ob['vendor']};
            else
                data_obj = {'category': data_ob['category']};
            console.log('id and prod seg of new product...', id, prod_seg, data_obj);
            $('.address').taggify(id, prod_seg, data_obj);
        }
      })
    }

    function setUp(addr_segs) {
      setUpAddress(addr_segs);
      bindMenuSnapping();
      $( "#selectable" ).selectable({ autoRefresh: true,filter:'span',selected: function( event, ui ) {
          showTag(event.pageX,event.pageY)
        }
      });

      $('.tag_list a').on("click", function(e) {
        console.log('i m clicked!');
        e.preventDefault();
        tagItem(this)
      });

      $('#clear-button').bind("click", function() {
        resetTags()
      });

      $('#submit-button').off().on('click', function() {
        if ($("span[tag]").length == $("span .address_element").length || $('input[type=checkbox]').is(':checked')) {

              var is_dang = $('#dangerous-goods').is(':checked');
              var is_xray = $('#x-ray').is(':checked');
              var is_dirty = $('#dirty-name').is(':checked');
              var is_skipped = false
              var tags = [];
              $.each($( "span .address_element"),function() {
                  if($(this).attr('tag') === undefined) {
                      tags = '';
                      return false;
                  }
                  tags.push([$(this).text(),$(this).attr('tag')])
              });
              sendTags(tags, is_dang, is_xray, is_dirty, is_skipped);
            $('#submit-button').notify('Tags saved, fetching new product name...', "success");
        } else {
            $.notify('Please tag everything or Skip this name.', { position:"bottom-right" });
        }
      });

      $('#skip-button').off().on('click', function() {
          var is_skipped = true
          sendTags(null, null, null, null, is_skipped);
          $('#skip-button').notify('Skipping product name', "info");
      });
    }

    setUp(segs)
  };
  return this
}( jQuery ));