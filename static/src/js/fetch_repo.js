odoo.define('odoo_infinity_app_store.fetch_repo', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;

    $(document).ready(function () {
        ajax.jsonRpc("/scanned_apps", 'call', {})
        .then(function (response) {
            console.log("Scanned APPS---------------------------------",response)

            var scannedAppsData = response
            renderScannedApps(scannedAppsData);
        });

        function fetchModuleInfo(sshUrl, listItem, repoId) {
            ajax.jsonRpc("/fetch_repository_content", 'call', {
                repo_id: repoId
            }).then(function (response) {
                alert("Apps Scan Successfully !!! ");
            });
        }

        function renderScannedApps(appsData) {
            var $appsSection = $('.my-apps-body');
            $appsSection.empty();
            var row;
            appsData.forEach(function (appData, index) {
                if (index % 4 === 0) {
                    // Start a new row
                    row = $('<div>').addClass('row m-4 mb-4');
                    $appsSection.append(row);
                }

                var appId = appData.id;
                console.log("APP ID",appId)

                var sshId = appData.ssh_repository_id;
                console.log("sshId ID",sshId)

                var productId = appData.product;
                console.log("productId ID",productId)

                // Create the card element
                var $appCard = $('<div>').addClass('card col-md-4 m-2').attr('data-app-id', appId).attr('data-ssh-id', sshId).attr('data-product-id', productId).css({
                    'width': '18rem',
                    'padding': '0px'
                });

                var $imageSection = $('<div>').addClass('card-img-top position-relative').css('height', '200px').hover(function () {
                    $(this).find('.card-description').fadeIn();
                }, function () {
                    $(this).find('.card-description').fadeOut();
                });
                var $cardBody = $('<div>').addClass('card-body');
                var $appIdDisplay = $('<p>').addClass('card-text').text('ID: ' + appId);

                // Image section
                $imageSection.append(
                    $('<img>').addClass('card-img').attr('src', appData.icon_image).css({
                        'object-fit': 'cover',
                        'height': '100%',
                    }),
                    $('<div>').addClass('card-description bg-dark text-white position-absolute bottom-0 start-0 end-0 p-2').css({
                        'opacity': '0.7',
                        'height': '-webkit-fill-available',
                        'text-align': 'center',
                    }).text(appData.description).hide()
                );
                $appCard.append($imageSection);

                var $appName = $('<h5>').addClass('card-title').text(appData.name).css({
                    'white-space': 'nowrap',
                    'overflow': 'hidden',
                    'text-overflow': 'ellipsis'
                });
                $cardBody.append($appName);

                var $companyName = $('<div>').addClass('col-8').text(appData.company_name).css({
                    'white-space': 'nowrap',
                    'overflow': 'hidden',
                    'text-overflow': 'ellipsis',
                    'font-size': '0.75rem'
                });
                var $row = $('<div>').addClass('row');
                $row.append(
                    $companyName,
                    $('<div>').addClass('col-4 text-end').text('$ ' + appData.price)
                );

                $appCard.on('click', function() {
                    var appId = $(this).attr('data-app-id');
                    var productId = $(this).attr('data-product-id');
                    window.location.href = '/app-details/' + appId +'/'+ productId ;
                });


//                $appCard.on('click', function() {
//                    var appId = $(this).attr('data-app-id');
//                    console.log("appId------------------",appId)
//                    window.location.href = '/app-details/' + appId;
//                });

                $cardBody.append($row);
                $cardBody.append($appIdDisplay);
                $appCard.append($cardBody);
                row.append($appCard);
            });
        }

        $("#apps_submit_repo_button").click(function () {
        $("#loading_gif").show();
            var ssh_url = $("#sshInput").val();
            var sshRegex = /^(ssh:\/\/)([^@]+)@([^\/]+)\/(.+)\.git(#(\d+(\.\d+)?))?$/;
            if (!sshRegex.test(ssh_url)) {
                alert("Please enter a valid SSH URL in the format: ssh://username@hostname/repository.git#branch");
                return;
                $("#loading_gif").hide();
            }

            var branch = ssh_url.match(/#(\d+(\.\d+)?)$/);
            if (!branch || !branch[1]) {
                alert("Please specify a branch name in the SSH URL.");
                return;
                $("#loading_gif").hide();
            }

            ajax.jsonRpc("/submit_ssh_url", 'call', {'ssh_url': ssh_url})
            .then(function(response) {
                alert("SSH key added successfully");
                window.location.href = '/my/dashboard/repositories';
                $("#loading_gif").hide();
            });
        });

        ajax.jsonRpc("/fetch_ssh_urls", 'call', {})
        .then(function(response) {
            $('#repositories-list').empty();

            response.forEach(function(data) {

            console.log("-----------------------------------Data-------------------------------", data)
                var sshUrl = data.ssh_url;
                var repoId = data.id;

                var listItem = $('<li>').addClass('list-group-item').css('height', 'auto').attr('data-repo-id', repoId);
                var inputGroup = $('<div>').addClass('apps_repo_input row');
                var inputCol = $('<div>').addClass('col-md-6');
                var buttonsCol = $('<div>').addClass('col-md-6 text-end');

                var sshInput = $('<input>').attr({'type': 'text', 'readonly': 'true'}).addClass('ssh_input form-control').val(sshUrl).data('ssh-url', sshUrl); // Set data attribute
                var buttonGroup = $('<div>').addClass('btn-group float-end');

                var editButton = $('<button>').addClass('btn edit_btn').css({'margin-right': '10px', 'border-radius': '8px'});
                var editIcon = $('<i>').addClass('fa fa-pencil');
                editButton.append(editIcon, ' Edit').click(function() {
                    sshInput.removeAttr('readonly');
                    editButton.hide();
                    saveButton.show();
                });

                var saveButton = $('<a>').addClass('btn save_btn').attr('href', '#').css({'margin-right': '10px', 'border-radius': '8px'}).hide().append($('<span>').addClass('fa fa-check'), ' Save');

                saveButton.click(function() {
                    var listItem = $(this).closest('li');
                    var newSshUrl = listItem.find('.ssh_input').val();
                    var repoId = listItem.data('repo-id');
                    console.log("==========newSshUrl===========", newSshUrl);
                    console.log("==========repoId===========", repoId);

                    editButton.show();
                    saveButton.hide();

                    ajax.jsonRpc("/update_ssh_url", 'call', {
                        repo_id: repoId,
                        new_ssh_url: newSshUrl
                    }).then(function(response) {
                        console.log('Response:', response);
                        if (response.success) {
                            listItem.find('.ssh_input').attr('readonly', true);
                        } else {
                            console.error('Error updating SSH URL');
                        }
                    });
                });

                var scanButton = $('<button>').addClass('btn scan_btn').css({'border-radius': '8px'});
                var scanIcon = $('<i>').addClass('fa fa-refresh');
                scanButton.append(scanIcon, ' Scan');

                scanButton.click(function () {
                    var listItem = $(this).closest('li');
                    var sshUrl = listItem.find('.ssh_input').val();
                    var repoId = listItem.data('repo-id');
                    console.log("Scanning repository:", repoId);
                    fetchModuleInfo(sshUrl, listItem, repoId);
                });

                var checkbox = $('<input>').addClass('scan_check').attr('type', 'checkbox').css({'margin-right': '30px', 'border-radius': '8px'});
                var activeButton = $('<button>').text('Active').addClass('btn active_btn btn-success').css({'margin-right': '10px', 'border-radius': '8px'}).hide();
                var draftButton = $('<button>').text('Draft').addClass('btn draft_btn btn-warning').css({'margin-right': '10px', 'border-radius': '8px'});
                var settingsButton = $('<a>').addClass('btn setting_btn').css({'margin-right': '10px', 'border-radius': '8px'});
                var settingsIcon = $('<i>').addClass('fa fa-gear');
                settingsButton.append(settingsIcon);

                var publishDiv = $('<div>').addClass('col-12 mb8 mt8 collapse show text-end');
                var publishButton = $('<a>').addClass('btn js_repo_publish fw_medium btn-primary').attr('href', '#').css({ 'margin-right': '10px', 'border-radius': '8px' }).hide().text('Publish all apps from this repo');
                var unpublishButton = $('<a>').addClass('btn js_repo_unpublish fw_medium btn-danger').attr('href', '#').css({ 'margin-right': '10px', 'border-radius': '8px' }).hide().text('Unpublish all apps from this repo');

                publishDiv.append(publishButton, unpublishButton);

                inputCol.append(sshInput);
                buttonsCol.append(editButton, saveButton, scanButton, checkbox, activeButton, draftButton, settingsButton);
                inputGroup.append(inputCol, buttonsCol);
                listItem.append(inputGroup, publishDiv);

                settingsButton.click(function () {
                    publishButton.toggle();
                    unpublishButton.toggle();
                });

                $('#repositories-list').append(listItem);
            });
        });

    });
});


