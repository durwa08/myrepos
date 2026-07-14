import api from "./api";

/**
 * Retrieve an in-progress attempt.
 *
 * @param {string} attemptId
 * @returns {Promise<Object>}
 */
export const getAttempt = async (attemptId) => {
  const response = await api.get(`/attempts/${attemptId}`);
  return response.data;
};

/**
 * Save an answer for a question.
 *
 * @param {string} attemptId
 * @param {string} questionId
 * @param {number} answerIndex
 * @returns {Promise<Object>}
 */
export const saveAnswer = async (
  attemptId,
  questionId,
  answerIndex
) => {
  const response = await api.patch(
    `/attempts/${attemptId}/answers`,
    {
      question_id: questionId,
      answer_index: answerIndex,
    }
  );

  return response.data;
};

/**
 * Submit an attempt.
 *
 * @param {string} attemptId
 * @returns {Promise<Object>}
 */
export const submitAttempt = async (attemptId) => {
  const response = await api.post(
    `/attempts/${attemptId}/submit`
  );

  return response.data;
};