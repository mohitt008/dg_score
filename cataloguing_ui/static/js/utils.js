function update_html(data) {
    $("#tag-products").css("display", "block");
    $("#org_prod_name").html(data['prod_name']);
    $("#vendor_name").html(data['vendor']);
    $("#vendor_name").attr("href", data['prod_url']);
    $("#selectable").html(data['prod_name']);
    $("#category").html(data['prod_cat']);
    $("#sub-category").html(data['prod_subcat']);

    if (data['is_dang'])
        $('#dangerous-goods').attr('checked','checked');
    if (data['is_xray'])
        $('#x-ray').attr('checked','checked');
    if (data['is_dirty'])
        $('#dirty-name').attr('checked','checked');
    if (data['tag_count'])
        $('#tag-count').html(data.tag_count);
    if (data['verify_count'])
        $('#verify-count').html(data.verify_count);

    attrs="";
    console.log(data['taglist']);
    if (!jQuery.isEmptyObject(data['taglist'])) {
      $.each(data['taglist'], function (attr, code) {
          attrs += '<a href="#" tagtype ="' + code + '"><span class="tag_text">' + attr + '</span></a>';
      });
    }
    $(".extra-attrs").html(attrs);
    id = data['id'];
    prod_seg = JSON.parse(data['prod_seg']);
}

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
                    attrs="";
                    $.each(data, function (attr, code) {
                      attrs += '<a href="#" tagtype ="' + code + '"><span class="tag_text">' + attr + '</span></a>';
                    });

                    $(".extra-attrs").html(attrs);
                    $('.address').taggify();
                }
            });
        }
    });
});

$(function () {
    $('#update-category').on("change", function () {
        var cat_id = $(this).find(':selected').val();
        $.ajax({
            url: '/cat-ui/get-subcats',
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