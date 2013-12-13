function checkPasswordMatch() {
    password = $("#password").val();
    confirmPassword = $("#password2").val();

    if (confirmPassword == '') {
      console.log("empty");
      $("#submit").attr('value', "Please fill the form");
      $("#submit").attr('disabled', true);
      $("#submit").attr('class', "btn btn-custom-disable"); 
    }else if (password != confirmPassword) {
      console.log("no match");
      $("#submit").attr('value', "Passwords do not match!");
      $("#submit").attr('disabled', true);
      $("#submit").attr('class', "btn btn-custom-disable"); 
    }else {
      console.log("match");
      $("#submit").attr('value', "Submit");
    	$("#submit").attr('disabled', false);
      $("#submit").attr('class', 'btn btn-custom');  
   	}
};

$("#password2").keyup(function(){checkPasswordMatch();console.log("called")});
$(document).ready(checkPasswordMatch());
