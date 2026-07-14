const passwordPattern =
  /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;

export const validateLogin = (values) => {
  const errors = {};

  if (!values.email.trim()) {
    errors.email = "Email is required";
  }

  if (!values.password.trim()) {
    errors.password = "Password is required";
  }

  return errors;
};

export const validateRegister = (values) => {
  const errors = {};

  if (values.username.trim().length < 3) {
    errors.username =
      "Username must be at least 3 characters";
  }

  if (!values.email.trim()) {
    errors.email = "Email is required";
  }

  if (!passwordPattern.test(values.password)) {
    errors.password =
      "Password must contain at least 8 characters, one uppercase letter, one number and one special character.";
  }

  return errors;
};