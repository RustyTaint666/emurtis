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
              axios(this.serviceURL+"/users/login", {
                method: 'POST',
                headers: {
                  'content-type': 'application/json',
                },
                data: {
                    "username": this.input.username,
                    "password": this.input.password
                },
              })
                .then(response => {
                    if (response.data.status == "success") {
                        this.authenticated = true;
                    }
                })
                .catch(error => {
                  throw error;
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