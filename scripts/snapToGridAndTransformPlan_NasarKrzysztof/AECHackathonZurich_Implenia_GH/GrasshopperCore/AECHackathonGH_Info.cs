using System;
using System.Drawing;

using Grasshopper.Kernel;

namespace AECHackathonZurich_Implenia_GH.GrasshopperCore
{
    public class AECHackathonGH_Info : GH_AssemblyInfo
    {
        public override string Name {
            get {
                return "AECHackathon Implenia";
            }
        }
        public override Bitmap Icon {
            get {
                return null;
            }
        }
        public override string Description {
            get {
                return "AEC Hackathon Zurich 2025 Implenia challange.";
            }
        }
        public override Guid Id {
            get {
                return new Guid("3b5d8ce2-55db-4481-8e7c-adedaf5397c6");
            }
        }

        public override string AuthorName {
            get {
                //Return a string identifying you or your company.
                return "Krzysztof Nazar";
            }
        }
        public override string AuthorContact {
            get {
                //Return a string representing your preferred contact details.
                return "";
            }
        }
        public override string Version {
            get {
                return System.Reflection.Assembly.GetExecutingAssembly().GetName().Version.ToString();
            }
        }

        public enum Group
        {
            Get = 0,
            Solve, 
            Algorithms
        }
    }
}
