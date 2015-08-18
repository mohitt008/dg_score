$(document).ready(function () {
    window.id;
    window.vendor;
    window.prod_seg;
    window.data_obj;

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
                            update_html(data);
                            data_obj = {'vendor': vendor};
                            $('.address').taggify();
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
                            update_html(data);
                            data_obj = {'category': data['prod_cat']};
                            $('.address').taggify();
                        }
                    }
                });
            }
        });
    });
});