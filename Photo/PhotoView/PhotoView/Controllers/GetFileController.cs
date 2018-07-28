using System.Web.Mvc;

namespace PhotoView.Controllers
{
	public class GetFileController : Controller
	{
		[HttpGet]
		public string Index(string token)
		{
			return "https://whoisalice.pagekite.me/Files/" + token + ".jpg";
		}
	}
}