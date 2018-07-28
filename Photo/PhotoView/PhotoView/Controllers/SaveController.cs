using System.Net;
using System.Web;
using System.Web.Mvc;

namespace PhotoView.Controllers
{
	public class SaveController : Controller
	{
		[HttpGet]
		public ActionResult Index(string token)
		{
            //TODO sdadsadsa
            if (string.IsNullOrEmpty(token))
                return View();

            ViewBag.Token = token;
			return View();
		}
 
		[HttpPost]
		public ActionResult Upload(HttpPostedFileBase upload, string token)
		{
			if(upload!=null)
			{
                // получаем имя файла
                string fileName = System.IO.Path.GetFileName(token + ".jpg");
				// сохраняем файл в папку Files в проекте
				upload.SaveAs(Server.MapPath("~/Files/" + fileName));
			}
			return RedirectToAction("Index");
		}
	}
}