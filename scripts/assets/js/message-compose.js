$(document).ready(function(){
	$(".mark_check_warning").hide();
	CKEDITOR.instances.message.setData($("#message_content").val());
	CKEDITOR.instances.message.on('change', function() { checkMessageType()});
	$("#submit-message").bind('click', function () {
		validateform();
		markAllChecks();
	});
	$("#email-type").on("change",function(){
		checkMessageType();
		console.log($("#email-type").val());
		if( $("#email-type").val() != "default" && $("#email-type").val() != "other"){
			$(".mark_check_warning").show();
		}
		else {			
			$(".mark_check_warning").hide();
		}			
	});
});


function markAllChecks () {	
	var checked = $(".hideShow.active input[type=checkbox]:checked");
	var unchecked = $(".hideShow.active input[type=checkbox]");
	var email_type = $("#email-type").val();
	if ( checked.length != unchecked.length && email_type != "default"){		
		$('#mark_all_checks').modal('show');
	}
}

function checkMessageType() {
	var checked = $(".hideShow.active input[type=checkbox]:checked");
	var unchecked = $(".hideShow.active input[type=checkbox]");
	var msg_type = $("#email-type").val();
	if (msg_type == "default"){
		$('#select_type_of_message').modal('show');
		$('#message_content_be_blank').modal('hide');
		determineErrorClass(false);
		return false;
	}	
	else if (msg_type == "other"){
		determineErrorClass(true);
		return true;
	}
	else {
		determineErrorClass(checked.length == unchecked.length);
		return (checked.length == unchecked.length);
	}
}

function determineErrorClass (argument) {
	if (argument == true) {
		$("#email-type").removeClass("parsley-error-list");
		$(".hideShow.active input:checkbox:not(:checked)").parent().removeClass("parsley-error-list");
		$(".hideShow.active input[type=checkbox]:checked").parent().removeClass("parsley-error-list");
		// $(".mark_check_warning").hide();
	}
	else {
		$("#email-type").addClass("parsley-error-list");
		$(".hideShow.active input:checkbox:not(:checked)").parent().addClass("parsley-error-list");
		$(".hideShow.active input[type=checkbox]:checked").parent().removeClass("parsley-error-list");
		// $(".mark_check_warning").show();
	}
	$(".hideShow.active input:checkbox:not(:checked)").bind("click", function () { 
		$(this).parent().removeClass("parsley-error-list");
		checkMessageType();
	});	
}


function validateform () {
	$('#message-form').parsley('validate');
	var form = $('#message-form').parsley('isValid') && validateMessage(CKEDITOR.instances.message.getData()) && checkMessageType();
	if(form){
		submitform(form);
	};
}

function strip (html) {
   var tmp = document.createElement("DIV");
   tmp.innerHTML = html;
   return tmp.textContent || tmp.innerText || "";
}

function validateMessage (message) {
	length = strip(message).length;
	if (length == 0) {	
		$('#message_content_be_blank').modal('show');
		$('#select_type_of_message').modal('hide');		
		return false;
	}
	else {
		return true;
	}
}

function submitform (form) {
	if (form == true){
		$("#final-message").val('<i>(This message was sent via the <a href="http://meltwater.org/incubator/strikeforce" target="_blank">MEST Strike Force platform</a>)</i><br><br><br><br>'+CKEDITOR.instances.message.getData());
		$("#message-form").submit();
	}
}
		