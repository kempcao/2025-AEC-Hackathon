using System;
using System.Drawing;

using Grasshopper.Kernel;

using AECHackathonZurich_Implenia_GH.Properties;

namespace AECHackathonZurich_Implenia_GH.GrasshopperCore
{
    public abstract class AECHackathonGH_Component : GH_Component
    {
        public AECHackathonGH_Component(string name, string nickname, string description, AECHackathonGH_Info.Group group)
            : base(name, nickname, description, "AECHack_Zurich", $"{(int)group:00}. {group}")
        {
        }

        protected override Bitmap Icon => Resources.component_icon;
    }
}
