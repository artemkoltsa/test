using System.Globalization;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace WhoIsAlice.Models
{
	
    public class Response
    {
        [JsonProperty("response")]
        public Answer Answer { get; set; }

        [JsonProperty("session")]
        public AnswerSession AnswerSession { get; set; }

        [JsonProperty("version")]
        public string Version { get; set; }
    }


	internal static class Converter
	{
		public static readonly JsonSerializerSettings Settings = new JsonSerializerSettings
		{
			MetadataPropertyHandling = MetadataPropertyHandling.Ignore,
			DateParseHandling = DateParseHandling.None,
			Converters = {
				new IsoDateTimeConverter { DateTimeStyles = DateTimeStyles.AssumeUniversal }
			}
		};
	}

    public static class Serialize
    {
        public static string ToJson(this Response self) => JsonConvert.SerializeObject(self, Converter.Settings);
    }
}