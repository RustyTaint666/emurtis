var app = new Vue({
    el: "#app",
  
    //------- data --------
    data: {
      serviceURL: "https://cs3103.cs.unb.ca:50035",
      authenticated: false,

      input: {
        username: "",
        password: ""
      },
    },
    methods: {
        // stuff goes here
        login() {
            if (this.input.username != "" && this.input.password != "") {
              axios
              .post(this.serviceURL+"/users/login", {
                  "username": this.input.username,
                  "password": this.input.password
              })
              .then(response => {
                  if (response.data.status == "success") {
                    this.authenticated = true;
                    axios
                    .post(this.serviceURL+"/users", {
                        "username": this.input.username
                    })
                  }
              })
              .catch(e => {
                  alert("The username or password was incorrect, try again");
                  this.input.password = "";
                  console.log(e);
              });
            } else {
              alert("A username and password must be present");
            }
        },

        logout() {
            axios
            .get(this.serviceURL+"/users/logout")
            .then(response => {
                if (response.data.status == "success") {
                    this.authenticated = false;
                }
            })
            .catch(e => {
              console.log(e);
            });
        },
    }
});