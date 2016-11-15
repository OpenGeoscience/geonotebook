function response (result, error, id) {
        // TODO validate taht result/error are mutually exclusive
  return {result: result,
    error: error,
    id: id };
}

export default response;
