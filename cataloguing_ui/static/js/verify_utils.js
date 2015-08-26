$(document).ready(function () {
  window.id;
  window.vendor;
  window.prod_seg;
  window.data_obj;
  window.tagged_data = "";

  $(function () {
    $("input[type=submit], button").button()
            .click(function (event) {
                event.preventDefault();
            });
    });

    $(function() {
        $( "#verify-button" ).click(function() {
            var vendor = $("#select-vendor").find(":selected").val();
            var cat_val = $("#select-category").find(":selected").val();
            var cat = $("#select-category").find(":selected").text();

            if( vendor=='-1' && cat_val=='-1' )
                $("#verify-button").notify('Please select a vendor or category first.');
            else {
                data_obj = {}
                if( vendor != '-1' )
                    data_obj['vendor'] = vendor;
                if( cat_val != '-1' )
                    data_obj['category'] = cat;
                console.log(data_obj);
                $.ajax({
                    url: '/cat-ui/verify-products',
                    dataType: 'json',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data_obj),
                    success: function (data) {
                        console.log(data);
                        if (data['error'])
                            $("#verify-button").notify(data['error']);
                        else {
                            update_html(data);
                            tagged_data = data['tags']
                            $('.address').taggify();
                        }
                    }
                });                         
            }
        });
    });
});