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

    $("#vendor-button1").click(function () {
      vendor = $("#select-vendor").find(":selected").val();
      if (vendor == '-1')
          $("#select-vendor").notify("Please select a Vendor first.", "error");
      else {
          $.ajax({
              url: '/cat-ui/get-vendor-products-verify',
              dataType: 'json',
              type: 'POST',
              contentType: 'application/json',
              data: JSON.stringify({ "vendor": vendor}),
              success: function (data) {
                  console.log('data received : ', data);
                  if (data['error'])
                      $("#select-vendor").notify(data['error']);
                  else {
                      update_html(data);
                      tagged_data = data['tags']
                      data_obj = {'vendor': vendor};
                      $('.address').taggify();

                  }
              }
          })
      }
    });

  $(function() {
    $( "#category-button1" ).click(function() {
        var cat = $("#select-category").find(":selected").text();
        var cat_id = $("#select-category").find(":selected").val();
        if(cat_id=='-1')
            $("#select-category").notify('Please select a category first.');
        else {
            $.ajax({
                url: '/cat-ui/get-category-products-verify',
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
                        tagged_data = data['tags']
                        $('.address').taggify();
                    }
                }
            });
        }
    });
  });
});