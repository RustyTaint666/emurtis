// register modal component
Vue.component("edit-modal", {
  template: "#edit-modal-template"
});

Vue.component("view-modal", {
  template: "#view-modal-template"
});

var app = new Vue({
    el: "#app",
  
    //------- data --------
    data: {
      serviceURL: "https://cs3103.cs.unb.ca:8003",
      authenticated: false,
      loggedIn: null,
      usersData: null,
      videosData: null,
      videoPath: null,
      videoFormat: null,
      editModal: false,
      viewModal: false,
      selectedVideo: null,
      selectedUsername: null,

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

        getVideosByUserId(user_id, username) {
          this.selectedUsername = username;
          axios
          .get(this.serviceURL+"/users/"+ user_id +"/videos")
          .then(response => {
            this.videosData = response.data.videos;
          })
          .catch(error => {
            console.log(error);
            this.videosData = null;
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
          bodyFormData.append('videoFile', videoFile[0]);

          axios
          .post(this.serviceURL+"/users/"+ user_id +"/videos", bodyFormData, {
            headers: { 
              "Content-Type": "multipart/form-data", 
              'vidName': updateVideo.name,
              'vidDesc': updateVideo.description 
            },
          })
          .then(response => {
            if (response.status === 201) {
              alert("Video successfully created.");
            }
          })
          .catch(error => {
            console.log(error);
          })

        },

        watchVideo(video) {
          this.showViewModal();
          this.setVideoPath(video.video);
          this.selectedVideo = video;
        },

        setVideoPath(videoFilePath) {
          this.videoFormat = videoFilePath.split(".")[1];
          this.videoPath = this.serviceURL + videoFilePath.split("/app")[1];
        },

        showEditModal() {
          this.editModal = true;
        },

        hideEditModal() {
          this.editModal = false;
        },

        showViewModal() {
          this.viewModal = true;
        },

        hideViewModal() {
          this.viewModal = false;
        },
    }
});