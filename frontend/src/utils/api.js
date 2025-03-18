export const uploadFile = async (file, endpoint, setPredictions, setError, setLoading) => {
    if (!file) {
      setError("Please upload a CSV file.");
      return;
    }
  
    setLoading(true);
    setError("");
    
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }
  
      const data = await response.json();
      if (data.predictions) {
        setPredictions(data.predictions);
      } else {
        setError("No predictions returned from the server.");
      }
    } catch (error) {
      setError("Error processing the request.");
      console.error("API Error:", error);
    } finally {
      setLoading(false);
    }
  };
  