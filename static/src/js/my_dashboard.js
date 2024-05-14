odoo.define('odoo_infinity_app_store.my_dashboard', function (require) {
    "use strict";
    $(document).ready(function(){
        $('.sidebar a').click(function(){
            var target = $(this).data('target');
            $('.section').hide();
            $('#' + target).show();
        });
    });
});
