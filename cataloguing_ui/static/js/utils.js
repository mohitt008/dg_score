$(document).ready(function () {
      window.q;
      window.id;
      window.attr_mapping_cat_filter
      window.attr_mapping_subcat_filter
      window.attr_id;
      window.vendor;
      window.prod_seg;
      window.data_obj;
      window.tagged_data = "";
      window.pid = null;
      window.is_undo = false;

      // $(function () {
      //     $("input[type=submit], button").button()
      //             .click(function (event) {
      //                 event.preventDefault();
      //             });
      // });
    $(function() {
        $( "#get-products-button" ).click(function() {

            var vendor = $("#select-vendor").find(":selected").val();
            var cat_filter = $("#specify-cat-filter").find(":selected").val();
            if( cat_filter == "-1" )
                var cat_val = "-1";
            else {
                var cat_val = $("#select-category").find(":selected").val();
                var cat = $("#select-category").find(":selected").text();
            }
            var subcat_val = $("#select-subcategory").find(":selected").val();
            if( subcat_val == "-1" )
                var subcat = null;
            else
                var subcat = $("#select-subcategory").find(":selected").text();
            var price_range_value = $("#select-price-range").find(":selected").val();
            var sPageURL = window.location.search.substring(1);
            sPageURL_split_list = sPageURL.split('=');

            if( vendor=='-1' && cat_val=='-1' && price_range_value=='-1' )
                $("#get-products-button").notify('Please select a vendor or category or price range first.');
            else {
                $("input[type=submit]").attr("disabled", "disabled")
                data_obj = {}
                if( vendor != '-1' )
                    data_obj['vendor'] = vendor;
                if( cat_val != '-1' && cat_val != null )
                    if( cat_filter == "dc" )
                        data_obj["category"] = cat;
                    else if( cat_filter == "vc" )
                        data_obj["vendor_cat"] = cat;
                if( subcat )
                    if( cat_filter == "dc")
                        data_obj['sub_category'] = subcat
                    else if( cat_filter == "vc" )
                        data_obj["vendor_subcat"] = subcat
                if( price_range_value != '-1' )
                    data_obj['price'] = price_range_value;
                q = sPageURL_split_list[1];
                data_obj[sPageURL_split_list[0]] = q;
                $.ajax({
                    url: '/cat-ui/get-products',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data_obj),
                    success: function (data) {
                        $("input[type=submit]").removeAttr("disabled")
                        if (data['error']) {
                            $("#get-products-button").notify(data['error']);
                        }
                        else {
                            update_html(data);
                            if ( q == 'verify' )
                                tagged_data = data['tags'];
                            else
                                tagged_data = "";
                            $('.address').taggify();
                        }
                    }
                });                         
            }
        });
    });

    $(function() {
        $( "#get-attribute-button" ).click(function() {

            var cat_val = $("#select-attr-mapping-cat").find(":selected").val();
            var cat_text = $("#select-attr-mapping-cat").find(":selected").text();
            var subcat_val = $("#select-attr-mapping-subcat").find(":selected").val();
            var subcat_text = $("#select-attr-mapping-subcat").find(":selected").text();
            if( subcat_val == undefined )
                subcat_val = '-1'
            if( cat_val=='-1' &&  subcat_val!='-1' )
                $("#get-attribute-button").notify('Please select a category for the selected sub-category.');
            else {
                $("input[type=submit]").attr("disabled", "disabled")
                data_obj = {}
                if ( cat_val == "-1" )
                    data_obj["cat"] = null
                else {
                    data_obj["cat"] = cat_text
                }
                if ( subcat_val == "-1" )
                    data_obj["subcat"] = null
                else {
                    data_obj["subcat"] = subcat_text
                }
                attr_mapping_cat_filter = data_obj["cat"]
                attr_mapping_subcat_filter = data_obj["subcat"]
                $.ajax({
                    url: '/cat-ui/get-attribute-details',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data_obj),
                    success: function (data) {
                        $("input[type=submit]").removeAttr("disabled")
                        if (data['error']) {
                            $("#get-attribute-button").notify(data['error']);
                        }
                        else {
                            update_html(data);
                            var allowed_attr_options = '<option value="-1">------ Select Core Attribute ------</option>';
                            $.each(data["allowed_attrs"], function (i, attr) {
                                allowed_attr_options += '<option value="' + attr + '">' + attr + '</option>';
                            });
                            allowed_attr_options += '<option value="null">None of these</option>';
                            $('#select-core-attribute').html(allowed_attr_options);
                        }
                    }
                });                         
            }
        });
    });

    $(function() {
        $( "#submit-core-attr-button" ).click(function() {

            var core_attr_val = $("#select-core-attribute").find(":selected").val();
            if( core_attr_val=='-1' )
                $("#submit-core-attr-button").notify('Please select a core attribute value before submitting.');
            else {
                $("input[type=submit]").attr("disabled", "disabled")
                data_obj = {};
                data_obj["attr_id"] = attr_id;
                data_obj["core_attr"] = core_attr_val;
                data_obj["cat_filter"] = attr_mapping_cat_filter;
                data_obj["subcat_filter"] = attr_mapping_subcat_filter;
                $.ajax({
                    url: '/cat-ui/set-attribute-mapping',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data_obj),
                    success: function (data) {
                        $("input[type=submit]").removeAttr("disabled")
                        if (data['error']) {
                            $("#submit-core-attr-button").notify(data['error']);
                        }
                        else {
                            $("#submit-core-attr-button").notify();
                            $('#submit-button').notify("Core attribute saved, fetching new attribute...", {
                                className:"success",
                                autoHide: true,
                                autoHideDelay: 1000
                            });
                            update_html(data);
                            var allowed_attr_options = '<option value="-1">------ Select Core Attribute ------</option>';
                            $.each(data["allowed_attrs"], function (i, attr) {
                                allowed_attr_options += '<option value="' + attr + '">' + attr + '</option>';
                            });
                            allowed_attr_options += '<option value=null>None of these</option>';
                            $('#select-core-attribute').html(allowed_attr_options);
                        }
                    }
                });                         
            }
        });
    });

    $(function () {
        $("#update-button").click(function () {
            var cat_id = $("#update-category").find(":selected").val();
            if (cat_id == '-1')
                $("#update-button").notify('Please select a category first.');
            else {
                var cat = $("#update-category").find(":selected").text();
                var subcat_id = $("#update-subcategory").find(":selected").val();
                var subcat;
                if (subcat_id == '-1')
                    subcat = null;
                else
                    var subcat = $("#update-subcategory").find(":selected").text();
                $.ajax({
                    url: '/cat-ui/change-category',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ "category": cat, "subcat": subcat, "id": id }),
                    success: function (data) {
                        $('#update-button').notify('Category Updated Successfully!', "success");
                        $('#update-button').notify("Category Updated Successfully!", {
                            className:"success",
                            autoHide: true,
                            autoHideDelay: 1500
                        });
                        attrs="";
                        $.each(data, function (attr, code) {
                          attrs += '<a href="#" tagtype ="' + code + '"><span class="tag_text">' + attr + '</span></a>';
                        });

                        $(".extra-attrs").html(attrs);
                        $("#category").html(cat);
                        $("#cat-new").show();
                        $("#sub-category").html(subcat);
                        $("#subcat-new").show();
                        $('.address').taggify();
                    }
                });
            }
        });
    });

    $(function () {
        $('#update-category').on("change", function () {
            var cat_id = $(this).find(':selected').val();
            if( cat_id != "-1" )
                get_subcats( cat_id, "#update-subcategory" )
        });
    });

    $(function () {
        $(".get-cats-class").on("change", function () {
            get_cats()
        });
    });

    $(function () {
        $("#select-category").on("change", function () {
            var cat_id = $(this).find(':selected').val();
            if( cat_id != "-1" )
                get_subcats( cat_id, "#select-subcategory" )
        });
    });

    $(function () {
        $("#select-hq-category").on("change", function () {
            var cat_name = $(this).find(':selected').val();
            if( cat_name != "-1" )
                get_hq_subcats( cat_name, "#select-hq-subcategory" )
        });
    });

    $(function () {
        $("#select-attr-mapping-cat").on("change", function () {
            var cat_id = $(this).find(':selected').val();
            if( cat_id != "-1" )
                get_attr_mapping_subcats( cat_id, "#select-attr-mapping-subcat" )
        });
    });

});

function update_html(data) {
    attr_id = data["attr_id"];
    $('input:checkbox').removeAttr('checked');
    $("#tag-products").css("display", "block");
    $("#map-attributes").css("display", "block");
    $("#page_attr_name").html(data['attr_name']);
    $("#page_attr_cat").html(data['cat']);
    $("#page_attr_subcat").html(data['subcat']);
    var sample_values = '';
    if (!jQuery.isEmptyObject(data['sample_values'])) {
        $.each(data['sample_values'],function(index){
            sample_values += '<li>'+this+'</li>';
        });
    }
    $("#page_attr_sample_values ul").html(sample_values);
    $("#org_prod_name").html(data['prod_name']);
    $("#vendor_name").html(data['vendor']);
    $("#vendor_name").attr("href", data['prod_url']);
    $("#selectable").html(data['prod_name']);
    $("#category").html(data['prod_cat']);
    $("#sub-category").html(data['prod_subcat']);
    $("#price").html(data['price']);
    $("#cat-new").hide();
    $("#subcat-new").hide();
    if (data['tagged_by'])
        $("#tagged-by").html(data['tagged_by']);
    if (data['is_dirty'])
        $('#dirty-name').prop("checked", true);
    if (data['tag_count'])
        $('#tag-count').html(data.tag_count);
    if (data['verify_count'])
        $('#verify-count').html(data.verify_count);
    attrs="";
    if (!jQuery.isEmptyObject(data['taglist'])) {
      $.each(data['taglist'], function (attr, code) {
          attrs += '<a href="#" tagtype ="' + code + '"><span class="tag_text">' + attr + '</span></a>';
      });
    }
    $(".extra-attrs").html(attrs);
    id = data['id'];
    if ('prod_seg' in data)
        prod_seg = JSON.parse(data['prod_seg']);
}

function get_cats() {
    $("#select-category").empty()
    $("#select-category").css("width", "")
    $("#select-category").prop('disabled', true);
    $("#select-subcategory").empty()
    $("#select-subcategory").css("width", "")
    $("#select-subcategory").prop('disabled', true);
    var vendor = $("#select-vendor").find(":selected").val();
    var cat_filter = $("#specify-cat-filter").find(":selected").val();

    if( cat_filter != "-1" ){

        if ( cat_filter=="vc" && (vendor=="All" || vendor=="-1") ) {
            $("#select-category").empty()
            $("#select-category").prop('disabled', true);
            $.notify("Invalid combination! Please select any specific vendor to get corresponding categories", {clickToHide: true});
        }
        else {
            $.ajax({
                url: '/cat-ui/get-cats',
                dataType: 'json',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({"cat_filter": cat_filter, "vendor": vendor}),
                success: function (data) {
                    $("#select-category").css("width", "150px");
                    $("#select-category").prop("disabled", false);
                    if (jQuery.isEmptyObject(data)) {
                        $("#select-category").empty()
                        $("#select-category").prop("disabled", true);
                    }
                    else {
                        var cat_options = '<option value="-1">--- Select Category ---</option>';
                        $.each(data, function (i, obj) {
                            $.each(obj._id, function (key, value) {
                                cat_options += '<option value="' + value + '">' + obj.category_name + '</option>';
                            });
                        });
                        $("#select-category").html(cat_options);
                    }
                }
            });
        }
    }
}

function get_subcats( cat_id, dropdown_id ) {
    $.ajax({
        url: '/cat-ui/get-subcats',
        dataType: 'json',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({"category_id": cat_id}),
        success: function (data) {
            if (jQuery.isEmptyObject(data)) {
                $(dropdown_id).html('<option value="-1">--- No Sub-Categories found ---</option>');
            }
            else {
                var subcat_options = '<option value="-1">--- Select Sub-Category ---</option>';
                $.each(data, function (i, obj) {
                    $.each(obj._id, function (key, value) {
                        subcat_options += '<option value="' + value + '">' + obj.category_name + '</option>';
                    });
                });
                $(dropdown_id).prop('disabled', false);
                $(dropdown_id).css("width", "200px");
                $(dropdown_id).html(subcat_options);
            }
        }
    });
}

function get_hq_subcats( cat_name, dropdown_id ) {
    $.ajax({
        url: '/cat-ui/get-hq-subcats',
        dataType: 'json',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({"cat": cat_name}),
        success: function (data) {
            if (jQuery.isEmptyObject(data)) {
                $(dropdown_id).prop('disabled', false);
                $(dropdown_id).html('<option value=null>------ No Sub-Categories found ------</option>');
            }
            else {
                var subcat_options = '<option value="-1">------ Select Sub-Category ------</option>';
                $.each(data, function (i, subcat) {
                    subcat_options += '<option value="' + subcat + '">' + subcat + '</option>';
                });
                subcat_options += '<option value=null>None of these</option>';
                $(dropdown_id).prop('disabled', false);
                $(dropdown_id).html(subcat_options);
            }
        }
    });
}

function get_attr_mapping_subcats( cat_id, dropdown_id ) {
    $.ajax({
        url: '/cat-ui/get-attr-mapping-subcats',
        dataType: 'json',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({"cat_id": cat_id}),
        success: function (data) {
            if (jQuery.isEmptyObject(data)) {
                $(dropdown_id).prop('disabled', false);
                $(dropdown_id).html('<option value="-1">------ No Sub-Categories found ------</option>');
            }
            else {
                var subcat_options = '<option value="-1">------ Select Sub-Category ------</option>';
                $.each(data, function (i, subcat) {
                    subcat_options += '<option value="' + subcat + '">' + subcat + '</option>';
                });
                $(dropdown_id).prop('disabled', false);
                $(dropdown_id).html(subcat_options);
            }
        }
    });
}