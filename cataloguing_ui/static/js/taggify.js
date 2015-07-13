(function ($) {
  $.fn.taggify = function (id, prod_seg, data_obj) {
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
          console.log(addr_elem.offset().top, addr_elem.outerHeight(false), addr_elem.offset().top + addr_elem.outerHeight(false));
        tooltip_obj.css({
          'position':'absolute',
          'display': 'block',
          'left' : addr_elem.offset().left + addr_elem.outerWidth( false )/2 - tooltip_obj.outerWidth( false )/2 - 215,
          'top' : addr_elem.offset().top - 10
        });
      })
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

    function sendTagsAJAX(tags, dang, xray, dirty) {
//      var date = new Date();
//      return_obj.epoch = date.getTime()
      data_obj['id']=id;
      data_obj['tags']=tags;
      data_obj['is_dang']=dang;
      data_obj['is_xray']=xray;
      data_obj['is_dirty']=dirty;
      return $.ajax({
        url: '/set-tags',
        dataType: 'json',
        type: 'POST', //make query POST
        contentType: 'application/json',
        data: JSON.stringify(data_obj)
      });
    }

    function sendTags() {
      var is_dang = $('#dangerous-goods').is(':checked');
      var is_xray = $('#x-ray').is(':checked');
      var is_dirty = $('#dirty-name').is(':checked');
      var tags = [];
      $.each($( "span .address_element"),function() {
          if($(this).attr('tag') === undefined) {
              tags = '';
              return false;
          }
          tags.push([$(this).text(),$(this).attr('tag')])
      });

      sendTagsAJAX(tags, is_dang, is_xray, is_dirty).done(function(data) {
        console.log("Successfuly Sent Data");
        console.log(data);
        if(data.error)
            alert(data.error);
        else {
            id = data['id'];
            //        total_tag_count = data.total_tag_count
            //        $("#total_tag_count").html(total_tag_count)
            resetTags();
            $('#org_prod_name').html(data.prod_name);
            $('#category').html(data.prod_cat);
            $('#sub-category').html(data.prod_subcat);
            $('#tag-count').html(data.tag_count);
            var segs = JSON.parse(data.prod_seg);
            setUpAddress(segs)
        }
      })
    }

    function setUp(addr_segs) {
      setUpAddress(addr_segs);
      bindMenuSnapping()
      $( "#selectable" ).selectable({ autoRefresh: true,filter:'span',selected: function( event, ui ) {
          showTag(event.pageX,event.pageY)
        }
      });

      $('.tag_list a').bind("click", function(e) {
        e.preventDefault();
        tagItem(this)
      });

      $('#clear-button').bind("click", function() {
        resetTags()
      });

      $('#submit-button').bind("click", function() {
        if ($("span[tag]").length == $("span .address_element").length) {
            sendTags();
            $('#submit-button').notify('Tags saved, fetching new product name...', "success");
        } else {
            alert("Please tag everything or Skip this name. ")
        }
      });

      $('#skip-button').bind("click", function() {
          sendTags();
          $('#submit-button').notify('Skipping product name', "info");
      });
    }

    setUp(prod_seg)
  };
  return this
}( jQuery ));