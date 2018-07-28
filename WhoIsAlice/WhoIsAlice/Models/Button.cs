using Newtonsoft.Json;

namespace WhoIsAlice.Models
{
	
	public class Button
	{
		[JsonProperty("title")]
		public string Title { get; set; }

		[JsonProperty("url")]
		public string Url { get; set; }

		[JsonProperty("hide")]
		public bool Hide { get; set; }
	}
}