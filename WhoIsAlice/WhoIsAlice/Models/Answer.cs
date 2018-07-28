using Newtonsoft.Json;

namespace WhoIsAlice.Models
{
	public class Answer
	{
		[JsonProperty("text")]
		public string Text { get; set; }

		[JsonProperty("tts")]
		public string Tts { get; set; }

		[JsonProperty("buttons")]
		public Button[] Buttons { get; set; }

		[JsonProperty("end_session")]
		public bool EndSession { get; set; }
	}
}