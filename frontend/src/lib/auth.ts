import Vue from "vue";

export function isConnected(http: any, onConnected: any, onDisconnected: any) {
  // Set access token
  var token = "Bearer " + localStorage.getItem("access_token");
  (Vue as any).http.headers.common["Authorization"] = token;

  // Look if the access token is still valid
  http.get("me").then(
    (response: any) => {
      onConnected(response);
    },
    (response: any) => {
      // If not, try refreshing token
      if (localStorage.getItem("refresh_token")) {
        refresh(http, onConnected, onDisconnected);
      } else {
        onDisconnected();
      }
    }
  );
}

export function refresh(http: any, onConnected: any, onDisconnected: any) {
  // Set refresh token
  var token = "Bearer " + localStorage.getItem("refresh_token");
  (Vue as any).http.headers.common["Authorization"] = token;

  http.post("auth/refresh").then(
    (response: any) => {
      response.json().then((data: { [x: string]: string }) => {
        console.log("Refresh successful");
        localStorage.setItem("access_token", data["access_token"]);
        onConnected();
      });
    },
    (response: any) => {
      logout();
      onDisconnected();
    }
  );
}

export function login(data: { [x: string]: string }) {
  localStorage.setItem("access_token", data["access_token"]);
  localStorage.setItem("refresh_token", data["refresh_token"]);
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  delete (Vue as any).http.headers.common["Authorization"];
}
