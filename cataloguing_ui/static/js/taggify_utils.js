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

    $(function() {
        $( "#tag-button" ).click(function() {
            var vendor = $("#select-vendor").find(":selected").val();
            var cat_val = $("#select-category").find(":selected").val();
            var cat = $("#select-category").find(":selected").text();

            if( vendor=='-1' && cat_val=='-1' )
                $("#tag-button").notify('Please select a vendor or category first.');
            else {
                data_obj = {}
                if( vendor != '-1' )
                    data_obj['vendor'] = vendor;
                if( cat_val != '-1' )
                    data_obj['category'] = cat;
                console.log(data_obj);
                $.ajax({
                    url: '/cat-ui/get-products',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data_obj),
                    success: function (data) {
                        console.log(data);
                        if (data['error'])
                            $("#tag-button").notify(data['error']);
                        else {
                            update_html(data);
                            $('.address').taggify();
                        }
                    }
                });                         
            }
        });
    });
});