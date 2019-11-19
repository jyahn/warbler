// const BASE_URL = 'https://warbler-vsha2.herokuapp.com';
const BASE_URL = 'http://localhost:5000';

$(document).ready(function () {
  $('#dm-form').on('submit', function (evt) {
    evt.preventDefault();
    let text = $('#dm-input').val();
    if (text.length > 1) {
      let conversationArr = document.URL.split('/');
      let conversationId = parseInt(conversationArr[conversationArr.length - 1]);
      $('#dm-form').trigger('reset');
      addDM(text, conversationId, function (resp) {
        console.log(resp);
      });
    }
  });
});

function addDM(text, conversationId, cb) {
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
