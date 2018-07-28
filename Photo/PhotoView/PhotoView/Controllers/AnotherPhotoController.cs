using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace PhotoView.Controllers
{
    public class AnotherPhotoController:Controller
    {
        public ActionResult Index()
        {
            return View();
        }
    }
}