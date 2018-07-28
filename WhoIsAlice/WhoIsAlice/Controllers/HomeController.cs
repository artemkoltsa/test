using System.Web.Mvc;
using WhoIsAlice.Models;

namespace WhoIsAlice.Controllers
{
	public class HomeController : Controller
	{
		[HttpPost]
		public ActionResult Index(Question question)
		{
	
		var	session = new AnswerSession
				{
					MessageId = 1,
					SessionId = "2eac4854-fce721f3-b845abba-20d60",
					UserId = "AC9WC3DF6FCE052E45A4566A48E6B7193774B84814CE49A922E163B8B29881DC"
				};
			

			var buttons = new[] { new Button{Hide = false, Title = "my button", Url = "https://ya.ru"}};

			var answer = new Answer
				{Buttons = buttons, EndSession = true, Text = $"Всем привет! Вернее Hello world!, вы спросили {question.Request.Command}", 
					Tts = $"Всем привет! Вернее Hello world!, вы спросили {question.Request.Command}"};
			
			var response = new Response
			{
				Answer = answer,
				AnswerSession = session,
				Version = "1.0"
			};

			return Content(response.ToJson(), "application/json");

		}

	}
}