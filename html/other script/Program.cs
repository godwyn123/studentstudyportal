using System.ComponentModel.DataAnnotations;

namespace SearchProApp.Models
{
    public class UserModel
    {
        [Key]
        public int Id { get; set; }

        [Required]
        public string Email { get; set; }

        [Required]
        public string Password { get; set; }

        public bool IsSubscribed { get; set; }
    }
}
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SearchProApp.Models;
using System.Linq;

namespace SearchProApp.Controllers
{
    public class HomeController : Controller
    {
        private readonly ApplicationDbContext _context;

        public HomeController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Displays the Subscription page
        public IActionResult Index()
        {
            return View();
        }

        // Handles Subscription Logic
        [HttpPost]
        public IActionResult Subscribe(UserModel user)
        {
            if (ModelState.IsValid)
            {
                _context.Add(user);
                _context.SaveChanges();
                return RedirectToAction("Search");
            }
            return View("Index");
        }

        // Displays the Search page
        public IActionResult Search()
        {
            return View();
        }

        // Handles Search Logic (Simulated)
        [HttpPost]
        public IActionResult SearchResults(string query)
        {
            var dummyData = new string[]
            {
                "How to code in HTML",
                "Best programming languages",
                "CSS design patterns",
                "JavaScript for beginners",
                "Building a web application"
            };

            var results = dummyData.Where(item => item.ToLower().Contains(query.ToLower())).ToList();
            return Json(results);
        }
    }
}
public void ConfigureServices(IServiceCollection services)
{
    services.AddDbContext<ApplicationDbContext>(options =>
        options.UseSqlServer(Configuration.GetConnectionString("DefaultConnection")));

    services.AddControllersWithViews();
}
