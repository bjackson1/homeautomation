
function setControlState(control, state) {
  var xhttp = new XMLHttpRequest();
  var newstate = 'on'
  if (state == 'on') { 
    newstate = 'off'
  }

  xhttp.onreadystatechange = function() {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
      var btn = document.getElementById("btn" + control);
      var lnk = document.getElementById("lnk" + control);
      
      var newstateid = xhttp.responseText;
      btn.src = '/static/power_button_' + newstateid + '.png';
      lnk.onclick = function() { setControlState(control, newstate); };
    }};
  xhttp.open("GET", "/control/" + control + "/" + state, true);
  xhttp.send();
  
  return false;
}


