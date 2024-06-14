function formSubmit(event) {
  if(!ValidateEmail()){
    event.preventDefault()
  }
  else{
    
  }
}

function unsubEmail(event) { //Gets Query string and submits unsub form
  event.preventDefault();
  const params = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
  });
  formSubmitV(params)

}

async function formSubmitV(query) {
  console.log("formSubmitV Called")
      const response = await fetch('https://formsubmit.co/ajax/faa81bd436bb81c7b8a89ee0b0bcad48', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
          },
          body: JSON.stringify({
              type: "unsubscribe",
              emailId: query.e,
              stateId: query.s,
              cityId: query.c
          })
      })
      
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.log(error));

    window.location.replace("https://rharvey6.github.io/WeatherNewsLetter/html/formSuccess.html")
}



function runEmailCheck () {
  emailText = d3.select("#Email").property("value")
  emailValid = d3.select("#emailValid")
  if(emailText == ""){
    emailValid.html("")
  }
  else if(isValidEmail(emailText)){
    emailValid.attr("style", "color: darkgreen").html("Valid email")
  } else{
    emailValid.attr("style", "color: darkred").html("Invalid email")
  }
  
}

function isValidEmail(email) {
  emailText = email
  var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  if(mailformat.test(emailText)){return true;}
    else {return false;}
}

d3.csv("../data/uscities.csv").then(function (data) {
  var cityStates = data;

  var emailBox = d3.select("#Email");
  emailBox.on("change", runEmailCheck)

  var formBox = d3.select("form")

  var stateButton = d3.select("#selectState"); //The select state box
  stateButton.on("click",setStates) //Whenever you click on the states box
  stateButton.on("change", runCities); //Whenver you change the states box

  hasRan = false //Only run once to prevent lag

  function setStates() {
    if(hasRan == false){
      filteredCities = data.sort(function (a,b) {return d3.ascending(a.State, b.State);}); //Sort states alphabetically
      hasRan = true
      d3.event.preventDefault(); //stops reload
      arr = []
      for (var i = 0; i<data.length;i++) { //Get all unique state names and put them in arr
        curState = data[i].State
        if(!(arr.includes(curState))){ //If curState not in arr
          arr.push(data[i].State); //Append to arr
          d3.select('#selectState').insert("option").html(curState)
        }
      }
    }
  }

  function runCities() {
    d3.select("#selectCity").html("")//clears the list
    d3.event.preventDefault(); //stops page refreshing
    var inputElement = d3.select("#selectState").property("value"); //Input from the state select box
    if(inputElement!='---'){
      var filteredCities = cityStates.filter(cityStates => cityStates.State.includes(inputElement)) //filters data for all cities with the given state
      filteredCities.sort(function (a,b) {return d3.ascending(a.City, b.City);});  //Sort cities alphabetically

      for (var i = 0; i<filteredCities.length;i++) { 
        city = filteredCities[i].City
        d3.select('#selectCity').insert("option").html(city)
      }
    }
  };

});