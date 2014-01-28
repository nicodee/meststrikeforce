$(document).ready(function () {
	$(".delete-company").bind("click", function(){
		deleteCompany($(this));
	});
});

function deleteCompany (argument) {
	var answer = confirm("This item will be deleted permanently. Do you want to continue?");

	if (answer){
		var company_id = argument.attr("data-id");
		var action = "delete";
		$.ajax("/admin/companies", {
			type: "POST",
			data: {action:action, company_id:company_id},
			success: handleDeleteResponse
		});
	}
}

function handleDeleteResponse (argument) {
	setTimeout("location.reload(true);",500);
}