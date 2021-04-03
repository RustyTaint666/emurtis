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
      updateVideo: {
        name: "",
        description: "",
        videoFile: null,
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
                        this.loggedIn = response.data.user_id;
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
          })
          .catch(error => {
            console.log(error);
          })
        },

        deleteVideo(video_id) {
          axios
          .delete(this.serviceURL+"/users/"+this.loggedIn+"/videos/"+video_id)
          .then(response => {
            if (response.status === 204) {
              this.getVideosByUserId(this.loggedIn);
              alert("Video successfully deleted.");
            }
          })
          .catch(error => {
            console.log(error);
          })
        },

        handleFileUpload(e) {
          var file = e.target.files || e.dataTransfer.files;
          videoFile = file;
        },

        postVideo(user_id, updateVideo) {
          var bodyFormData = new FormData();
          bodyFormData.append('video', videoFile);

          axios({
            method: "post",
            url: this.serviceURL+"/users/"+ user_id +"/videos",
            data: bodyFormData,
            headers: { 
              "Content-Type": "multipart/form-data", 
              'vidName': updateVideo.name,
              'vidDesc': updateVideo.description 
            },
          })
          .then(response => {
            alert("Video successfully created.");
          })
          .catch(error => {
            console.log(error);
          })

        },
    }
});