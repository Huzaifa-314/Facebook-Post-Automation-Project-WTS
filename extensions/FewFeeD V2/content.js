function e(t) {
  return new Promise((n) => {
    if (document.querySelector(t)) return n(document.querySelector(t));
    let i = new MutationObserver((i) => {
      document.querySelector(t) && n(document.querySelector(t));
    });
    i.observe(document.body, {
      attributes: !0,
      characterData: !0,
      childList: !0,
      subtree: !0,
    });
  });
}
chrome.runtime.sendMessage({ type: "INIT_SET_COOKIE" }, function (t) {
  localStorage.setItem("fewfeed", JSON.stringify({ cookie: t, version: 15 }));
}),
  e("#fewfeed-set-anon").then((t) => {
    t.addEventListener("click", () => {
      chrome.runtime.sendMessage({ type: "SET_ANONYMOUS" }, function (t) {});
    });
  }),
  e("#fewfeed-add-login").then((t) => {
    t.addEventListener("click", () => {
      chrome.runtime.sendMessage({ type: "LOGIN_NEW_ACC" }, function (t) {});
    });
  }),
  e("#fewfeed-reels-wipe").then((t) => {
    t.addEventListener("click", () => {
      chrome.runtime.sendMessage(
        { type: "WIPE_REELS", body: {} },
        function (n) {
          t.value = n;
          let i = new Event("keyup", { bubbles: !0, cancelable: !1 });
          t.dispatchEvent(i);
        }
      );
    });
  }),
  e("#fewfeed-accounts-add").then((t) => {
    t.addEventListener("click", () => {
      chrome.runtime.sendMessage(
        { type: "SET_MULTIPLE_HEADER", body: t.value },
        function (n) {
          t.value = n;
          let i = new Event("keyup", { bubbles: !0, cancelable: !1 });
          t.dispatchEvent(i);
        }
      );
    });
  }),
  e("#fewfeed-reel-add").then((t) => {
    t.addEventListener("click", () => {
      chrome.runtime.sendMessage(
        { type: "SET_REEL_DATA", body: t.value },
        function (n) {
          t.value = n;
          let i = new Event("keyup", { bubbles: !0, cancelable: !1 });
          t.dispatchEvent(i);
        }
      );
    });
  }),
  e("#fewfeed-cookie-add").then((t) => {
    t.addEventListener("click", () => {});
  }),
  e("#fewfeed-click").then((t) => {
    t.addEventListener("click", () => {
      chrome.runtime.sendMessage(
        {
          type: "SET_RAW_COOKIE",
          body: localStorage.getItem("main_cookie") || {},
        },
        function (n) {
          (t.value = n),
            localStorage.setItem(
              "fewfeed",
              JSON.stringify({ cookie: n, version: 2 })
            );
          let i = new Event("keyup", { bubbles: !0, cancelable: !1 });
          t.dispatchEvent(i);
        }
      );
    });
  });