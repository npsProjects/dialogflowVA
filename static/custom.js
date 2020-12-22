// Came with the chatbot template code
// This is dealing with the messages in the chatbox
var Message;
Message = function (arg) {
    this.text = arg.text, this.message_side = arg.message_side;
    this.draw = function (_this) {
        return function () {
            var $message;
            $message = $($('.message_template').clone().html());
            $message.addClass(_this.message_side).find('.text').html(_this.text);
            $('.messages').append($message);
            return setTimeout(function () {
                return $message.addClass('appeared');
            }, 0);
        };
    }(this);
    return this;
};

var getMessageText, message_side, sendMessage;
message_side = 'right';
getMessageText = function () {
    var $message_input;
    $message_input = $('.message_input');
    return $message_input.val();
};
sendMessage = function (text) {
    var $messages, message;
    if (text.trim() === '') {
        return;
    }
    $('.message_input').val('');
    $messages = $('.messages');
    message_side = message_side === 'left' ? 'right' : 'left';
    message = new Message({
        text: text,
        message_side: message_side
    });
    message.draw();
    return $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
};
// Button Functionallity, could not make it work for some reason.
// $('.send_message').click(function (e) {
//     sendMessage(getMessageText());
//     submit_message(getMessageText());
// });

// $('.message_input').keyup(function (e) {
//     if (e.which === 13) {
//         submit_message(getMessageText());
//         return sendMessage(getMessageText());
//     }
// });
// Keep track on which tables are on the screen


// Same as button, but works with enter
$('#target').on('submit', function(e){
        e.preventDefault();
        const input_message = $('#input_message').val()

        if (!input_message) {
          return
        }

        submit_message(input_message);
});

var x;
// Functionallity of popups
function togglePopup(popupNumber){
  document.getElementById(popupNumber).classList.toggle("active");
}
// SPecify the table you want and provide the info
function updateTable(answer, table){
  $("#"+table+" tr").remove();
  answer = answer.replace(/\'/gi, '');
  answer = answer.replace(/\'/gi, '');
  answerAll = answer.split('(');
  answer = answerAll[0].split(',');
  if ($("#"+table+" thead").length == 0) {
      $("#"+table).append("<thead></thead>");
  }
  tableContent = "<tr>"
  for (i = 1; i < answer.length-1; i++) {
      tableContent = (tableContent + "<th>"+ answer[i] + "</th>")
      lengthTable = i;
  }
  tableContent =  (tableContent + "</tr>")
  $("#"+table+" thead").append(tableContent)
  // 12 is the max length we allow of the table (Should be modified at one point)
  for (j = 1; j < Math.min(12,answerAll.length); j++) {
    answer = answerAll[j].split(',');
    if ($("#"+table+" tbody").length == 0) {
        $("#"+table).append("<tbody></tbody>");
    }
    tableContent = "<tr>"
    for (i = 0; i < lengthTable; i++) {
        tableContent = (tableContent + "<td>"+ answer[i] + "</td>")
    }
    tableContent =  (tableContent + "</tr>")
    $("#"+table+" tbody").append(tableContent)
  }

  clickableTableHeading()

}
// Sending a message
function submit_message(message) {
      $.post( "/send_message", {message: message}, handle_response);
      // Show it on screen
      sendMessage(message);
      function handle_response(data) {
        // Parse the resonse. We check if we are dealing with type message.
        answer = data.message;
        console.log(answer);
        answer = answer.replace(/\[/gi, '');
        answer = answer.replace(/\]/gi, '');
        answer = answer.replace(/\)/gi, '');
        splitAnswer = answer.split('|');
        splitAnswer[0] = splitAnswer[0].replace(/\'/gi, '');
        splitAnswer[0] = splitAnswer[0].replace(/\,/gi, '');
        console.log(splitAnswer[0]);

        // Based on type of response, deal with
        // Type 1: Just a table
        if (splitAnswer[0].trim() == 'Type1'){
          // Popup logic
          if (x==1){
              togglePopup("popup-1")
          }
          else if(x==2){
              togglePopup("popup-1")
              togglePopup("popup-2")
          }
          x = 1;
          togglePopup("popup-1")

          // Update table
          updateTable(splitAnswer[1], "table1")

          // Parse and send message
          splitAnswer[2] = splitAnswer[2].replace(/\'/gi, '');
          splitAnswer[2] = splitAnswer[2].replace(/\,/gi, '');
          splitAnswer[2] = splitAnswer[2].replace(/\"/gi, '');
          sendMessage(splitAnswer[2].trim())

          // Table heading
          splitAnswer[3] = splitAnswer[3].replace(/\'/gi, '');
          splitAnswer[3] = splitAnswer[3].replace(/\,/gi, '');
          document.getElementById("firstTable").innerHTML = splitAnswer[3];
        }
        // Type2 : 2 tables
        else if (splitAnswer[0].trim() == 'Type2') {
          // Popup logic
          if (x==1){
              togglePopup("popup-1")
          }
          else if(x==2){
              togglePopup("popup-1")
              togglePopup("popup-2")
          }
          x = 2;
          togglePopup("popup-1")
          togglePopup("popup-2")

          // Update table with  data
          updateTable(splitAnswer[1], "table1")
          updateTable(splitAnswer[2], "table2")

          // Parse the message
          splitAnswer[3] = splitAnswer[3].replace(/\'/gi, '');
          splitAnswer[3] = splitAnswer[3].replace(/\,/gi, '');
          splitAnswer[3] = splitAnswer[3].replace(/\"/gi, '');
          sendMessage(splitAnswer[3].trim())

          // Table headings
          splitAnswer[4] = splitAnswer[4].replace(/\'/gi, '');
          splitAnswer[4] = splitAnswer[4].replace(/\,/gi, '');
          splitAnswer[5] = splitAnswer[5].replace(/\'/gi, '');
          splitAnswer[5] = splitAnswer[5].replace(/\,/gi, '');
          document.getElementById("firstTable").innerHTML = splitAnswer[4];
          document.getElementById("secondTable").innerHTML = splitAnswer[5];

          clickableTableHeading()
        }
        else if (splitAnswer[0].trim() == 'Type3') {
          // Toggle popup logic
          if (x==1){
              togglePopup("popup-1")
          }
          else if(x==2){
              togglePopup("popup-1")
              togglePopup("popup-2")
          }
          x = 2;
          togglePopup("popup-1")
          togglePopup("popup-2")

          // Update first table
          updateTable(splitAnswer[1], "table1")

          // Remove second table if existing in order to add graph to popup
          $("#table2 tr").remove();
          document.getElementById("secondTable").innerHTML = "";

          // Add message response message
          splitAnswer[2] = splitAnswer[2].replace(/\'/gi, '');
          splitAnswer[2] = splitAnswer[2].replace(/\,/gi, '');
          splitAnswer[2] = splitAnswer[2].replace(/\"/gi, '');
          sendMessage(splitAnswer[2].trim())

          // Add table name
          splitAnswer[4] = splitAnswer[4].replace(/\'/gi, '');
          splitAnswer[4] = splitAnswer[4].replace(/\,/gi, '');
          document.getElementById("firstTable").innerHTML = splitAnswer[4];

          // Edit graph data
          splitAnswer[3] = splitAnswer[3].replace(/\,/gi, '');
          splitAnswer[3] = splitAnswer[3].replace(/\(/gi, '');
          graphData = splitAnswer[3].split("\'")
          // Modify graph data to correct format
          data = [];
          interData = [];
          for (i = 2; i < graphData.length-1; i= i + 2) {
            interData = [];
            interData.push(graphData[i]);
            interData.push(graphData[i+1]);
            data.push(interData);
          }
          var chart = anychart.column();
          // add data to chart
          chart.data(data);
          // set the chart title and draw it
          chart.title("Pending invoices per payer");
          chart.container("container");
          chart.draw();
        }
        // Type4: Email fill in
        else if (splitAnswer[0].trim() == 'Type4') {
            sendMessage("I prepared an email for you.")
            for (i = 0; i<=7; i++){
              splitAnswer[i] = splitAnswer[i].replace(/\'/gi, '');
              splitAnswer[i] = splitAnswer[i].replace(/\,/gi, '');
              splitAnswer[i] = splitAnswer[i].replace(/\"/gi, '');
            }
            sendEmail(getMailtoUrl (splitAnswer[2], splitAnswer[3], "Hi <"+ splitAnswer[1] + ">, \r\n Just checking to see if you are receiving our emails. \r\n I wanted to let you know that we have not yet received a payments for invoice number <" + splitAnswer[3] +"> which was due on  <" + splitAnswer[4] + "> with an amount of <"+ splitAnswer[5]+">. \r\n If you have made the payment already please contact our customer support on www.dummylink.com \r\n \r\n Best regards, \r\n<" + splitAnswer[6] +"> \r\n<"+ splitAnswer[7]+" >"));
        }
        else{
              sendMessage(answer)
        }
      }
  }
// Simple submit for initial text
function submit_first_message(message) {
        $.post( "/send_first_message", {message: message}, handle_first_response);
        function handle_first_response(data) {
          sendMessage(data);
        }
    }
// Send an email template
function getMailtoUrl(to, subject, body) {
    var args = [];
    if (typeof subject !== 'undefined') {
        args.push('subject=' + encodeURIComponent(subject));
    }
    if (typeof body !== 'undefined') {
        args.push('body=' + encodeURIComponent(body))
    }

    var url = 'mailto:' + encodeURIComponent(to);
    if (args.length > 0) {
        url += '?' + args.join('&');
    }
    return url;
}
function sendEmail(address) {
    window.location.href = address;//'mailto:' + address;
}
// Make the headings clickable so we can sort
function clickableTableHeading(){
    document.querySelectorAll(".table-sortable th").forEach(headerCell => {
        headerCell.addEventListener("click", () => {
            const tableElement = headerCell.parentElement.parentElement.parentElement;
            const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
            const currentIsAscending = headerCell.classList.contains("th-sort-asc");

            sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
        });
    });
}
/**
 * Sorts a HTML table.
 *
 * @param {HTMLTableElement} table The table to sort
 * @param {number} column The index of the column to sort
 * @param {boolean} asc Determines if the sorting will be in ascending
 */
function sortTableByColumn(table, column, asc = true) {
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));

    // Sort each row
    if (column !== 3 &&  column !== 4 && column !== 5) {
            sortedRows = rows.sort((a, b) => {
            const aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
            const bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();

            return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
        })
    }
    else {
            sortedRows = rows.sort((a, b) => {
            const aColPrice = parseFloat(a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim().replace('$', ''));
            const bColPrice = parseFloat(b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim().replace('$', ''));

            return aColPrice > bColPrice ? (1 * dirModifier) : (-1 * dirModifier);
        })
    }


    // Remove all existing TRs from the table
    while (tBody.firstChild) {
        tBody.removeChild(tBody.firstChild);
    }

    // Re-add the newly sorted rows
    tBody.append(...sortedRows);

    // Remember how the column is currently sorted
    table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-desc", !asc);
}
// submit this to get the first message
submit_first_message("first Message ");
