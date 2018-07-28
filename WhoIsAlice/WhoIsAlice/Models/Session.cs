using Newtonsoft.Json;

namespace WhoIsAlice.Models
{
	
	public class AnswerSession
	{
		[JsonProperty("session_id")]
		public string SessionId { get; set; }

		[JsonProperty("message_id")]
		public long MessageId { get; set; }

		[JsonProperty("user_id")]
		public string UserId { get; set; }
	}
}