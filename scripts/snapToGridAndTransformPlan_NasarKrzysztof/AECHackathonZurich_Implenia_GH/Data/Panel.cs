using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Eto.Forms;

using Newtonsoft.Json;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Data
{
    public class Panel
    {
        [JsonProperty("panel_type")]
        public string PanelType { get; set; }

        [JsonProperty("start_point")]
        public List<double> StartPoint { get; set; }

        [JsonProperty("end_point")]
        public List<double> EndPoint { get; set; }

        [JsonProperty("height")]
        public double Height { get; set; }

        [JsonProperty("thickness")]
        public double Thickness { get; set; }

        [JsonProperty("room")]
        public string Room { get; set; }

        [JsonProperty("apartment")]
        public string Apartment { get; set; }

        /// <summary>
        /// Creates a deep copy of the Panel object.
        /// </summary>
        public Panel DeepCopy()
        {
            return new Panel
            {
                PanelType = this.PanelType,
                StartPoint = this.StartPoint != null ? new List<double>(this.StartPoint) : null,
                EndPoint = this.EndPoint != null ? new List<double>(this.EndPoint) : null,
                Height = this.Height,
                Thickness = this.Thickness,
                Room = this.Room,
                Apartment = this.Apartment
            };
        }

        public Line ToLine()
        {
            return new Line(StartPoint[0], StartPoint[1], StartPoint[2], EndPoint[0], EndPoint[1], EndPoint[2]);
        }

        public void SetStartPoint(Point3d point)
        {
            StartPoint[0] = point.X;
            StartPoint[1] = point.Y;
            StartPoint[2] = point.Z;
        }

        public void SetEndPoint(Point3d point)
        {
            EndPoint[0] = point.X;
            EndPoint[1] = point.Y;
            EndPoint[2] = point.Z;
        }

        public void SetAxis(Line line)
        {
            SetStartPoint(line.From);
            SetEndPoint(line.To);
        }
    }
}
