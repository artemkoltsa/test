using System.Globalization;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace WhoIsAlice.Models
{
	public partial class Question
    {
        [JsonProperty("meta")]
        public Meta Meta { get; set; }

        [JsonProperty("request")]
        public Request Request { get; set; }

        [JsonProperty("session")]
        public QuestionSession QuestionSession { get; set; }

        [JsonProperty("version")]
        public string Version { get; set; }
    }

    

    public class Request
    {
        [JsonProperty("command")]
        public string Command { get; set; }

        [JsonProperty("original_utterance")]
        public string OriginalUtterance { get; set; }

        [JsonProperty("type")]
        public string Type { get; set; }

        [JsonProperty("markup")]
        public Markup Markup { get; set; }
    }

    public class Markup
    {
        [JsonProperty("dangerous_context")]
        public bool DangerousContext { get; set; }
    }


    public class QuestionSession
    {
        [JsonProperty("new")]
        public bool New { get; set; }

        [JsonProperty("message_id")]
        public long MessageId { get; set; }

        [JsonProperty("session_id")]
        public string SessionId { get; set; }

        [JsonProperty("skill_id")]
        public string SkillId { get; set; }

        [JsonProperty("user_id")]
        public string UserId { get; set; }
    }

    public partial class Question
    {
        public static Question FromJson(string json) => JsonConvert.DeserializeObject<Question>(json, Converter.Settings);
    }
}