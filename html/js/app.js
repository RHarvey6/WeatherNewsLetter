d3.csv("uscities.csv").then(function (data) {
  var cityStates = data;

  var button = d3.select("#selectState"); //The select state box
  button.on("click",setStates) //Whenever you click on the states box
  button.on("change", runEnter); //Whenver you change the states box

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

  function runEnter() {
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