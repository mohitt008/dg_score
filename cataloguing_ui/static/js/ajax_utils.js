$(document).ready(function () {
    var id;
    var vendor;
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
                alert('Select a Vendor first.');
            else {
                $.ajax({
                    url: '/get-vendor-products',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ "vendor": vendor}),
                    success: function (data) {
                        if (data['error'])
                            alert(data['error']);
                        else {
                            $("#tag-products").css("display", "block");
                            $("#org_prod_name").html(data['prod_name']);
                            $("#selectable").html(data['prod_name']);
                            $("#category").html(data['prod_cat']);
                            $("#sub-category").html(data['prod_subcat']);
                            var prod_seg = JSON.parse(data['prod_seg']);
                            id = data['id'];
                            var data_obj = {'vendor': vendor}
                            $('.address').taggify(id, prod_seg, data_obj)
                        }
                    }
                })
            }
        });
    });

    $(function () {
        $("#update-button").click(function () {
            var cat_id = $("#update-category").find(":selected").val();
            var subcat_id = $("#update-subcategory").find(":selected").val();
//            console.log(cat, subcat);
            if (cat_id == '-1')
                alert('Please select a category first.');
            else {
                var cat = $("#update-category").find(":selected").text();
                var subcat;
                if (subcat_id == '-1')
                    subcat = null;
                else
                    var subcat = $("#update-category").find(":selected").text();
                $.ajax({
                    url: '/change-category',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ "category": cat, "subcat": subcat, "id": id }),
                    success: function (data) {
                        alert(data['message']);
//                    $("#msg").append(data['message']);
                    }
                });
            }
        });
    });

    $(function () {
        $('#update-category').on("change", function () {
            var cat_id = $(this).find(':selected').val();
            $.ajax({
                url: '/get-subcats',
                dataType: 'json',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({"category_id": cat_id}),
                success: function (data) {
                    console.log(data)
                    $("#update-subcategory").prop('disabled', false);
                    if (jQuery.isEmptyObject(data)) {
                        $("#update-subcategory").html('<option value="-1">--- No Sub-Categories found ---</option>');
                        $("#update-subcategory").prop('disabled', true);
                    } else {
                        var subcat_options = '<option value="-1">-------- Select Sub-Category --------</option>';
                        $.each(data, function (i, obj) {
                            $.each(obj._id, function (key, value) {
                                subcat_options += '<option value="' + value + '">' + obj.category_name + '</option>';
                            });
                        });
                        $("#update-subcategory").html(subcat_options);
                    }
                }
            });
        });
    });

    $(function() {
        $( "#category-button" ).click(function() {
            var cat = $("#select-category").find(":selected").text();
            $.ajax({
                url: '/get-category-products',
                dataType: 'json',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({"category": cat}),
                success: function (data) {
                    console.log(data);
                    if (data['error'])
                        alert(data['error']);
                    else {
                        $("#tag-products").css("display", "block");
                        $("#org_prod_name").html(data['prod_name']);
                        $("#selectable").html(data['prod_name']);
                        $("#category").html(data['prod_cat']);
                        $("#sub-category").html(data['prod_subcat']);
                        var prod_seg = JSON.parse(data['prod_seg']);
                        var data_obj = {'category': data['prod_cat']}
                        $('.address').taggify(data['id'], prod_seg, data_obj);
                    }
                }
            });
        });
    });
});