using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Newtonsoft.Json;

using Rhino.DocObjects;
using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Data
{
    public class BuildingData
    {
        [JsonProperty("panels")]
        public PanelsData Panels { get; set; }

        [JsonProperty("spaces")]
        public Dictionary<string, Space> Spaces { get; set; }

        [JsonProperty("applied_transform_matrix")]
        public double[,] AppliedTransformMatrix { get; set; }

        [JsonProperty("transform_matrix_to_the_original")]
        public double[,] TransformMatrixToTheOriginal { get; set; }

        public BuildingData DeepCopy()
        {
            string json = JsonConvert.SerializeObject(this);
            return JsonConvert.DeserializeObject<BuildingData>(json);
        }

        public void SaveAppliedTransformMatrix(Transform transform)
        {
            AppliedTransformMatrix = new double[4, 4];
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 4; j++) {
                    AppliedTransformMatrix[i, j] = transform[i, j];
                }
            }

        }
        public Transform GetAppliedTransformMatrix()
        {
            if (AppliedTransformMatrix == null) {
                return Transform.Identity;
            }
            Transform t = new Transform();
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 4; j++) {
                    t[i, j] = AppliedTransformMatrix[i, j];
                }
            }
            return t;
        }

        public void SaveTransformMatrixToTheOriginal(Transform transform)
        {
            TransformMatrixToTheOriginal = new double[4, 4];
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 4; j++) {
                    TransformMatrixToTheOriginal[i, j] = transform[i,j];
                }
            }
        }

        public Transform GetTransformMatrixToTheOriginal()
        {
            if (TransformMatrixToTheOriginal == null) {
                return Transform.Identity;
            }
            Transform t = new Transform();
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 4; j++) {
                    t[i, j] = TransformMatrixToTheOriginal[i, j];
                }
            }
            return t;
        }
    }
}
