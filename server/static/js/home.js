//on click method for make it custom
$("#show_the_custom").click(function () {
	if ( $( "#short_url_input" ).is( ":hidden" ) ) {
	    $( "#short_url_input" ).slideDown( "slow" );
	    $("#onlyForm").attr("action","/server/shorts");
	    $("#show_the_custom").text("Make it Auto!");
	} else {
	    //$( "#short_url_input" ).hide();
	    $( "#short_url_input" ).slideUp( "slow" );
	    $('#submit_button').attr('disabled', false); 
	    $('#submit_button').attr('class', "btn btn-custom"); 
	    $("#onlyForm").attr("action","/server/autoshort");
	    $("#show_the_custom").text("Make it Custom!");
	    
	  }
	validation();
	});


//input validation
/*
-Make sure long is filled 
-if custom is on then short should be filled as well
-long should have http:// at the begining
...	
*/
var disableSubmit = function(){
	$('#submit_button').attr('disabled', true);
	$('#submit_button').attr('class', "btn btn-custom-disable"); 
}
var enableSubmit = function(){
	$('#submit_button').attr('disabled', false);
    $('#submit_button').attr('class', "btn btn-custom");  
}


function shortValidation(inputString) {
  	var objRegExp  = /^([a-zA-Z]|[0-9])+$/;
  	return objRegExp.test(inputString);
}
function validation(e){

	if ($('#shorturl').is(':visible')) {
		if ($('#shorturl').val().length!=0 && shortValidation($('#shorturl').val()) && $('#longurl').val().length!=0) {
			enableSubmit();
		}else{
			disableSubmit();
		};
	}else{
		if ($('#longurl').val().length==0) {
			disableSubmit();	
		}else{
			enableSubmit();
		};		
	};
};


d3.selectAll("p").style("color", function() {
  return "hsl(" + Math.random() * 360 + ",100%,50%)";
});


$(document).ready(function(){
  validation();
	$("#longurl").keyup(function(e){validation()});
	$("#shorturl").keyup(function(e){validation()});
});