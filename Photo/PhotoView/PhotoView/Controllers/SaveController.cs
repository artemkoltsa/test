using System.Net;
using System.Web;
using System.Web.Mvc;

namespace PhotoView.Controllers
{
	public class SaveController : Controller
	{
		[HttpGet]
		public ActionResult Index()
		{
			return View();
		}
 
		[HttpPost]
		public ActionResult Upload(HttpPostedFileBase upload)
		{
			if(upload!=null)
			{
				// получаем имя файла
				string fileName = System.IO.Path.GetFileName(upload.FileName);
				// сохраняем файл в папку Files в проекте
				upload.SaveAs(Server.MapPath("~/Files/" + fileName));
			}
			return RedirectToAction("Index");
		}
	}
}