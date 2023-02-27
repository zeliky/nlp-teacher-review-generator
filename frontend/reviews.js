
function get_mbti(){
    var mbti = ""
    var grades = {}
    mbti+=load_selection(grades, "E","I")
    mbti+=load_selection(grades, "S","N")
    mbti+=load_selection(grades,"T","F")
    mbti+=load_selection(grades,"J","P")
    return mbti
}
function spinner(){
    return `<div class="spinner-border text-primary" role="status"></div>`
}

function load_mbti_characteristics(){
    var mbti = get_mbti()
    $.get('/mbti_characteristics/?mbti='+mbti)
      .done(function (data) {
          console.log(data)
        var i=1
        var txt = '';
        data['characteristics'].forEach(function (chr) {
             if (chr.length >4) {
                txt += `<div class="form-check form-check-inline"><label class="form-check-label" >${chr}</label><input class="form-check-input" type="checkbox" value="${chr}" ></div>`
            }
        });
        $('#characteristics').html(txt)

    });
    return false

}
function suggest(type){
     switch(type){
        case 'behaviour':
            problem = $('#behavior_problem').val()
            break;
        case 'subject':
            problem = $('#low_subject').val()
            break;
    }
    var formData = {
        'type': type,
        'mbti': get_mbti(),
        'problem': problem
    }
     $('#'+type+'_ideas').html(spinner())
    $.ajax({
      type: "POST",
      contentType: 'application/json',
      url: "/suggest/",
      data: JSON.stringify(formData),
    }).done(function (data) {
        var i=1
        var txt = '';
        data['ideas'].forEach(function (idea) {
             if (idea.length >4) {
                txt += `<div class="form-check"><label class="form-check-label" >${idea}</label><input class="form-check-input" type="checkbox" value="${idea}" ></div>`
            }
        });
        $('#'+type+'_ideas').html(txt)

    });
    return false
}
function toggle_mbti(selected,unselected){
        var selected_bg_color = '#cbcbcb'
        $('.mbti-col.'+ selected).css("background-color",selected_bg_color)
        $('.mbti-col.'+ unselected).css("background-color","#ffffff")
    }

function load_selection(grades, opt1,opt2){
    selector = "#"+opt1.toLowerCase() + opt2.toLowerCase() + "_range"
    grade = parseInt($(selector).val())
    if (grade <0) {
        selected = opt1
        unselected = opt2
    }else {
        selected = opt2
        unselected = opt1
    }
    grades[selected] = Math.abs(grade)
    toggle_mbti(selected,unselected)
    return selected
}
$(document).ready(function () {
          $('#suggest-subject').click(function(){
            return suggest('subject')
          })
          $('#suggest-behaviour').click(function(){
            return  suggest('behaviour')
          })
          $('#suggest-characteristics').click(function(){
            return  load_mbti_characteristics()
          })

load_mbti_characteristics

          $('#response-section').hide()
          $('#loading-spinner').hide()
          $('.mbti-col').css("background-color",'#ffffff')
          $("#review-form").submit(function (event) {
            var mbti = ""
            var grades = {}
            mbti+=load_selection(grades, "E","I")
            mbti+=load_selection(grades, "S","N")
            mbti+=load_selection(grades,"T","F")
            mbti+=load_selection(grades,"J","P")


            var formData = {
              first_name: $("#first_name").val(),
              mbti: mbti,
              grades: grades,
              good_characteristic: $("#good_characteristic").val(),
              great_achievement: $("#great_achievement").val(),
              behavior_problem: $("#behavior_problem").val(),
              low_subject: $("#low_subject").val(),
              leader_to_quote: $("#leader_to_quote").val(),
            };
            $('#submit-section').hide()
            $('#response-section').hide()
            $('#loading-spinner').show()
            $.ajax({
              type: "POST",
              contentType: 'application/json',
              url: "/generate_review/",
              data: JSON.stringify(formData),
            }).done(function (data) {
              $('#submit-section').show()
              $('#loading-spinner').hide()
                var i=1
                data['reviews'].forEach(function (x) {
                     $('#response-text-' + (i)).val(x.text);
                     $('#original-text-' + (i)).html(x.original);
                     i++
                });
              $('#response-section').show()
              $('#response-text').focus()
              console.log(data);
            });

            event.preventDefault();
          });
        });