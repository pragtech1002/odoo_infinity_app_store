
//odoo.define('odoo_infinity_app_store.auth_signup_register_form', function (require) {
//    'use strict';
//
//    var ajax = require('web.ajax');
//    console.log('is jasssssss')
//    $(document).ready(function () {
//
//     $(document).on('submit', '.oe_signup_form', function (ev) {
//            console.log('Submit event triggered');
//            ev.preventDefault();
//            console.log('in javascript')
//            var form = $(this);
//            var login = form.find('input[name="login"]').val(); // Assuming email is entered in the "login" field
//            console.log('email--',login)
//            var name = form.find('input[name="name"]').val(); // Assuming email is entered in the "login" field
//            console.log('name--',name)
//            var password = form.find('input[name="password"]').val();
//            console.log('password--',password)
//
//            // Check for existing email using Ajax request
//            ajax.jsonRpc('/web/signup/submit', 'call', {
//                login: login,
//                name:name,
//                password: password
//
//            }).then(function (result) {
//                if (result) {
//                    alert('An employee with this email already exists.');
//                } else {
//                    form[0].submit();
//                }
//            });
//        });
//    });
//});




odoo.define('odoo_infinity_app_store.auth_signup_register_form', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {
        $(document).on('submit', '.oe_signup_form', function (ev) {
    ev.preventDefault();
    var form = $(this);
    var login = form.find('input[name="login"]').val();
    var name = form.find('input[name="name"]').val();
    var password = form.find('input[name="password"]').val();
    var confirmPassword = form.find('input[name="confirm_password"]').val();
    var github_account_name = form.find('input[name="github_account_name"]').val();

    // Check if the GitHub account exists
   checkGitHubAccountExists(github_account_name)

         checkGitHubAccountExists(github_account_name)
            .then(function (exists) {
                console.log('GitHub account existence:', exists);
                if (!exists) {
                    alert('GitHub account does not exist. Please enter a valid GitHub username.');
                } else {
                    // Proceed with form submission if GitHub account exists
                    ajax.jsonRpc('/web/signup/submit', 'call', {
                        login: login,
                        name: name,
                        password: password,
                        github_account_name: github_account_name
                    }).then(function (result) {
                        if (result.error) {
                            alert(result.error);
                        } else {
                            alert('User registered successfully!');
                            window.location.href = "/web/login";
                        }
                    });
                }
            })
            .catch(function (error) {
                console.error('Error checking GitHub account:', error);
                alert('An error occurred while checking the GitHub account. Please try again later.');
            });
    });



//        click on copy button data save code
         $('.copy-icon').click(function() {
        // Get the SSH key value from the input field
        var sshKey = $('#ssh-key-input').val();

        // Create a temporary input element
        var tempInput = document.createElement('input');
        tempInput.setAttribute('type', 'text');
        tempInput.setAttribute('value', sshKey);
        document.body.appendChild(tempInput);

        // Select and copy the value
        tempInput.select();
        document.execCommand('copy');

        // Remove the temporary input element
        document.body.removeChild(tempInput);

        // Provide feedback to the user
        alert('SSH key copied to clipboard!');
    });
     $('#download-link').click(function() {
        var sshKey = $('#ssh-key-input').val();
        var blob = new Blob([sshKey], { type: 'text/plain' });
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'public_ssh_key.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    });
    });
});

function checkGitHubAccountExists(username) {
    console.log('Checking GitHub account:', username);
    return new Promise(function (resolve, reject) {
        // Make an AJAX request to GitHub API to check if the user exists
        $.ajax({
            url: 'https://api.github.com/users/' + username,
            type: 'GET',
            success: function (response) {
                console.log('GitHub API response:', response);
                // If the response contains data, the user exists
                resolve(true);
            },
            error: function (xhr, status, error) {
                // If the response status is 404 (Not Found), the user does not exist
                if (xhr.status === 404) {
                    resolve(false);
                } else {
                    // Handle other errors
                    reject(error);
                }
            }
        });
    });
}
