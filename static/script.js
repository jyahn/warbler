// const BASE_URL = 'https://warbler-ja.herokuapp.com';
const BASE_URL = 'http://localhost:5000';

$(document).ready(function () {
  $('#dm-form').on('submit', function (evt) {
    evt.preventDefault();
    let text = $('#dm-input').val();
    console.log("text is ", text);
    if (text.length > 1) {
      let conversationArr = document.URL.split('/');
      console.log(conversationArr);
      let conversationId = parseInt(conversationArr[conversationArr.length - 1]);
      $('#dm-form').trigger('reset');
      addDM(text, conversationId, function (resp) {
        console.log(resp);
      });
    }
  });
});

function addDM(text, conversationId, cb) {
  console.log("YES")
  $.ajax({
    method: 'POST',
    url: `${BASE_URL}/conversations/${conversationId}/dm/add`,
    contentType: 'application/json',
    data: JSON.stringify({ text }),
    success: response => {
      cb(response);
    }
  });
  // append it to the dom
  $('.dm-list').append($(`<div class="my dm-row ml-auto">${text}</div>`));
}
