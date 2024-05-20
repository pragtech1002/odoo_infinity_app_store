odoo.define('your_module_name.add_cart', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function() {
        // Listen for form submission
        $('form.oe_import.apps_buy_form').on('submit', function(event) {
            // Prevent the default form submission behavior
            event.preventDefault();

            // Get the product ID from the form data
            var productId = $(this).find('input[name="product_id"]').val();
            console.log("ID-----------------------------",productId)

            // Perform an AJAX request to add the product to the cart
            ajax.jsonRpc('/shop/cart/update', 'call', {
                'product_id': productId,
                // Add any additional data you need to send
            }).then(function(response) {
                // Redirect to the cart view after adding the product to the cart
                window.location.href = '/shop/app_cart';
            });
        });
    });

});
