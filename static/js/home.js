
$(document).ready(function () {
    $("#submitBtn").click(onClickSubmit);
});

function onClickSubmit() {
    var country = document.getElementById("ctyInput").value;
    var duration = document.getElementById("durInput").value;
    var style = document.getElementById("stInput").value;
    //로그인 기능
    if (country && duration && style) {
        var data = { "country": country, "duration": duration, "style": style };

        $.ajax({
            url: "/token",
            type: "post",
            contentType: "application/JSON",
            data: JSON.stringify(data),
            success: printIt,
            error: function (e) {
                alert("fail!");
            }
        });
    } else {
        alert('Please fill out all fields.');
    }

}

function printIt(plans) {
    const plansContainer = $('#plansContainer');
    plansContainer.empty();  // Clear previous plans if any

    const itinerary = parseItinerary(plans['plan']);
    itinerary.shift();
    itinerary.forEach(dayPlan => {
        const planItem = $('<div class="planItem"></div>').html(dayPlan);
        plansContainer.append(planItem);
    });
}
function parseItinerary(paragraph) {
    const dayPattern = /Day \d+:/g;
    paragraph = paragraph.toString();
    const days = paragraph.split(dayPattern).filter(day => day.trim().length > 0);
    const dayMatches = paragraph.match(dayPattern);

    return days.map((day, index) => {
        if (index != 0) {
            return `<h3>${dayMatches[index - 1]}</h3><ul>${day.split('\n').filter(line => line.trim().startsWith('*')).map(line => `<li>${line.substring(1).trim()}</li>`).join('')}</ul>`;
        }
    });
}