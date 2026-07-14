import api from "./api";

/**
 * Base64-encodes a password before it's sent to the server.
 *
 * Wraps btoa() with encodeURIComponent/unescape so this also works
 * correctly for passwords containing non-ASCII characters (accents,
 * emoji, etc.), which plain btoa() would otherwise throw on.
 *
 * Note: this is encoding, not encryption or hashing - it's reversible
 * by anyone who intercepts it. Real protection against interception
 * comes from HTTPS. This step exists only to avoid sending the raw
 * password string as-is.
 */
const encodePassword = (password) => {
  return btoa(unescape(encodeURIComponent(password)));
};

export const loginUser = async (data) => {
  const payload = { ...data, password: encodePassword(data.password) };
  const response = await api.post("/auth/login", payload);
  return response.data;
};

export const registerUser = async (data) => {
  const payload = { ...data, password: encodePassword(data.password) };
  const response = await api.post("/auth/register", payload);
  return response.data;
};

export const checkEmail = async (email) => {
  const response = await api.get("/auth/check-email", {
    params: { email },
  });

  return response.data;
};