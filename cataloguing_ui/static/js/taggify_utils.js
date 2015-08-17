$(document).ready(function () {
    window.id;
    window.vendor;
    var attrs="";
    window.prod_seg;
    var data_obj;

    $(function () {
        $("input[type=submit], button").button()
                .click(function (event) {
                    event.preventDefault();
                });
    });

    $(function () {
        $("#vendor-button").click(function () {
            vendor = $("#select-vendor").find(":selected").val();
            if (vendor == '-1')
                $("#select-vendor").notify("Please select a Vendor first.", "error");
            else {
                $.ajax({
                    url: '/cat-ui/get-vendor-products',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ "vendor": vendor}),
                    success: function (data) {
                        if (data['error'])
                            $("#select-vendor").notify(data['error']);
                        else {
                            $("#tag-products").css("display", "block");
                            $("#org_prod_name").html(data['prod_name']);
                            $("#vendor_name").html(data['vendor']);
                            $("#vendor_name").attr("href", data['prod_url']);
                            $("#selectable").html(data['prod_name']);
                            $("#category").html(data['prod_cat']);
                            $("#sub-category").html(data['prod_subcat']);

                            id = data['id'];
                            prod_seg = JSON.parse(data['prod_seg']);
                            data_obj = {'vendor': vendor};
                            attrs="";
                            console.log(data['taglist']);
                            if (!jQuery.isEmptyObject(data['taglist'])) {
                                $.each(data['taglist'], function (attr, code) {
                                    attrs += '<a href="#" tagtype ="' + code + '"><span class="tag_text">' + attr + '</span></a>';
                                });
                            }

                            $(".extra-attrs").html(attrs);
                            $('.address').taggify(id, prod_seg, data_obj);

                        }
                    }
                })
            }
        });
    });

    $(function() {
        $( "#category-button" ).click(function() {
            var cat = $("#select-category").find(":selected").text();
            var cat_id = $("#select-category").find(":selected").val();
            if(cat_id=='-1')
                $("#select-category").notify('Please select a category first.');
            else {
                $.ajax({
                    url: '/cat-ui/get-category-products',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({"category": cat}),
                    success: function (data) {
                        console.log(data);
                        if (data['error'])
                            $("#select-category").notify(data['error']);
                        else {
                            $("#tag-products").css("display", "block");
                            $("#org_prod_name").html(data['prod_name']);
                            $("#vendor_name").html(data['vendor']);
                            $("#vendor_name").attr("href", data['prod_url']);
                            $("#selectable").html(data['prod_name']);
                            $("#category").html(data['prod_cat']);
                            $("#sub-category").html(data['prod_subcat']);

                            id = data['id'];
                            prod_seg = JSON.parse(data['prod_seg']);
                            data_obj = {'category': data['prod_cat']};
                            attrs="";
                            console.log(data['taglist']);
                            if (!jQuery.isEmptyObject(data['taglist'])) {
                                $.each(data['taglist'], function (attr, code) {
                                    attrs += '<a href="#" tagtype ="' + code + '"><span class="tag_text">' + attr + '</span></a>';
                                });
                            }

                            $(".extra-attrs").html(attrs);
                            $('.address').taggify(id, prod_seg, data_obj);
                        }
                    }
                });
            }
        });
    });
});