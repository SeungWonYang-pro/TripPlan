
$(document).ready(function () {
    $("#submitBtn").click(onClickLogin);
});

function onClickLogin() {
    var country = document.getElementById("ctyInput").value;
    var duration = document.getElementById("durInput").value;
    var style = document.getElementById("stInput").value;
    var data = { "country":country, "duration":duration,"style":style};
    //로그인 기능
    $.ajax({
        url: "/token",
        type: "post",
        contentType: "application/JSON",
        data: JSON.stringify(data),
        success: printIt,
        error: function(e){
            alert("fail!");
        }
    })

}

function printIt(plans)
{
    plans['plan'].forEach(item => {
        console.log(item);
    });
}