//odoo.define('odoo_infinity_app_store.version_click_handler', function (require) {
//    "use strict";
//
//    var ajax = require('web.ajax');
//
//    $(document).on('click', '.version-link', function (event) {
//        event.preventDefault();
//        var $link = $(this);
//        var version = $link.data('version');
//        var technicalName = $link.data('technical-name');
//        var appId = $link.data('app-id');
//        var sshId = $link.data('ssh-id');
//        var productId = $link.data('product-id');
//
//        // Check if the data attributes are correctly retrieved
//        console.log('version------------------------', version);
//        console.log('technicalName------------------', technicalName);
//        console.log('appId--------------------------', appId);
//        console.log('sshId--------------------------', sshId);
//        console.log('productId----------------------', productId);
//
//        // Proceed with the AJAX call if all necessary data attributes are present
//        if (version && technicalName) {
//            ajax.jsonRpc('/get_product_details', 'call', {
//                version: version,
//                technical_name: technicalName
//            }).then(function (data) {
//                // Handle the returned data here
//                console.log('data------------------', data);
//                if (data) {
//                    // Display the data in a modal or on a new page as needed
//                    window.location.href = '/app-details/' + data.app_id + '/' + data.product_id;
//                } else {
//                    console.error('No data returned for the provided parameters.');
//                }
//            }).catch(function (error) {
//                console.error('Error:', error);
//            });
//        } else {
//            console.error('Missing required data attributes.');
//        }
//    });
//});
