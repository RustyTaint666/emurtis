var app = new Vue({
    el: "#app",
  
    //------- data --------
    data: {
      serviceURL: "https://cs3103.cs.unb.ca:50035",
      authenticated: false,
      loggedIn: null,
      usersData: null,
      videosData: null,

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
                        this.createUser(this.input.username);
                        this.getUsers();
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

        createUser(username) {
            axios
            .post(this.serviceURL+"/users", {
              'username': username
            })
            .then(response => {
              this.loggedIn = response.data.user_id;
            })
            .catch(error => {
              console.log(error);
            })
        },

        getUsers() {
            axios
            .get(this.serviceURL+"/users")
            .then(response => {
              this.usersData = response.data.users;

            })
            .catch(error => {
              console.log(error);
            })
        },

        getVideosByUserId(user_id) {
          axios
          .get(this.serviceURL+"/users/"+ user_id +"/videos")
          .then(response => {
            this.videosData = response.data.videos;
            //Vue.set(this.videosData, user_id, response.data.videos)
          })
          .catch(error => {
            console.log(error);
          })
        }
    }
});